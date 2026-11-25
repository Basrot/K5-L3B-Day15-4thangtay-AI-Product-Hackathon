# Nối model vào `codebase/ai.py` — ví dụ

> Làm ở guide bước 3.3 — **việc dễ kẹt nhất, nên xong tối Thứ Sáu 27/11 trước khi ngủ** (sáng Thứ Bảy 28/11 không có lớp). Kẹt quá 20 phút → hỏi ngay.

Nhóm dùng ví dụ dưới đây để `call_model()` trong `codebase/ai.py` gọi model thật: đọc key, gửi yêu cầu, lấy câu trả lời và **số token** (đơn vị model dùng để đếm chữ; giá tính theo token). Ví dụ chỉ minh hoạ cách kết nối, không có lời giải cho bài nào: prompt và luồng do nhóm tự viết (`codebase/agent.py`).

**BTC không cấp API key.** Nhóm dùng gói miễn phí hoặc tài khoản của nhóm.

Đọc theo thứ tự: mục 1 chọn nhà cung cấp, lấy key → mục 2 điền `.env` → mục 3 chép khung vào `ai.py` → mục 4 chọn **một** ví dụ → mục 5 thử → mục 6 khi gặp lỗi.

> **Ba ví dụ đã chạy với key thật ngày 25/11/2026** (bộ câu thử 20 câu, 0 lỗi): **Claude** (mục 4.3, `claude-haiku-5-5`), **OpenAI** (mục 4.2, `gpt-5.4-nano`) và **Ollama** (mục 4.4, `gemma4:12b`, `llama3.2:3b`). Chép vào là chạy, chỉ cần `.env` đúng. Ví dụ **Gemini** (mục 4.1) cần nhóm điền 2 chỗ theo tài liệu chính thức, mất khoảng 20 phút; hoặc đi đường nhanh ở mục 4.0 (dùng được cho mọi nhà cung cấp).

## 1. Chọn nhà cung cấp, lấy key

Bảng dưới tóm tắt mục 2 của bảng giá model (`further-reading/model-prices.md` trong repo đề), đọc trên trang chính thức ngày 25/11/2026.

| Lựa chọn | Tốn tiền? | Lưu ý |
|---|---|---|
| **Gemini API gói miễn phí** (Google AI Studio) | Không | Trang giá ghi "Free of charge" cho gemini-3.1-flash-lite, gemini-3.5-flash-lite, gemini-3.8-flash, gemini-4-hydrogen, gemma-4. Giới hạn số lượt theo từng project (xem trong AI Studio); chạy bộ câu thử 20–30 câu và mô phỏng 50 phiên có thể chạm giới hạn |
| **Credit dùng thử Anthropic** (Claude) | Không, trong mức credit | Trang chỉ ghi "New users receive free credits to test the API", **không ghi số tiền**. Cần thẻ hay không: chưa kiểm |
| **Model mở chạy trên máy** (Ollama + Gemma 4) | Không | Bản `gemma4:e2b` nặng 4,6–7,5 GB, `gemma4:e4b` 6,6–9,5 GB (theo ollama.com/library/gemma4). **Rất chậm:** BTC đo trên máy Mac ngày 25/11, `gemma4:12b` mất 43–165 giây mỗi câu, nên 20–30 câu thử cộng 50 phiên mô phỏng không kịp trong hackathon. Model nhỏ (`llama3.2:3b`, ~4 giây/câu) thì nhanh nhưng trả lời kém hẳn. Hợp để thử luồng, không hợp làm model chính |
| **Tài khoản trả tiền của nhóm** (OpenAI, Anthropic, Google, DeepSeek…) | Có | OpenAI: trang giá không có gói miễn phí API. Nhóm tự nạp tiền nếu dùng |

**Lấy key gói miễn phí:**

1. Chọn một nhà cung cấp có gói miễn phí trong bảng trên (ví dụ Google AI Studio cho Gemini).
2. Đăng nhập bằng **tài khoản cá nhân**: tài khoản của trường / công ty có thể bị chặn tạo key.
3. Tìm mục tạo API key trong trang của nhà cung cấp (với Gemini: Google AI Studio), tạo **1** key.
4. Dán key vào file `.env` (mục 2). **Không** dán key vào chat, slide, code, repo.

**Không lấy được key:** thử nhà cung cấp khác có gói miễn phí, hoặc chạy model trên máy (Ollama + Gemma 4). Vẫn kẹt thì **báo lab coach trước khi rời lớp 19:30 Thứ Sáu 27/11**.

> **Gói miễn phí có thể dùng dữ liệu gửi lên để cải thiện sản phẩm** (trang giá Gemini ghi ở gói miễn phí: "Content used to improve our products"). **Data trong `data/` của bộ đề được đưa vào thoải mái**: data pre-class đã ẩn danh và không có câu chữ học viên viết, data training-ops là giả lập. Dữ liệu người thật nhóm tự thu (ghi chép phỏng vấn, câu trả lời khảo sát, tin Discord) thì chỉ gửi **bản đã bỏ tên hoặc đoạn đã viết lại**.

Gợi ý: chưa có tài khoản trả tiền thì bắt đầu bằng Gemini gói miễn phí. Mỗi nhóm chỉ cần **một** người nối model; người khác dùng chung `ai.py` qua repo (key thì mỗi máy tự để trong `.env` riêng).

## 2. Điền `.env`

Chép `.env.example` thành `.env` (Windows: `copy .env.example .env` · macOS/Linux: `cp .env.example .env`), điền 3 dòng. Ví dụ với Gemini *(ví dụ)*:

```
MODEL_PROVIDER=gemini
MODEL_NAME=gemini-3.5-flash-lite
API_KEY=<key của nhóm, không dấu ngoặc kép>
```

- `codebase/ai.py` đã có sẵn đoạn đọc `.env` (hàm `load_env`) và ba biến `MODEL_PROVIDER`, `MODEL_NAME`, `API_KEY` — không cần cài thêm thư viện.
- `.env` chưa có `MODEL_PROVIDER` (hoặc `MODEL_PROVIDER=fake`) → `ai.py` chạy **chế độ giả**: trả câu giả cố định, token 0. Dùng được cho bản khung trước CP2, nhưng `run.py eval` / `run.py simulate` sẽ không tính lượt đó.
- `MODEL_NAME` ghi **mã gọi API** chính thức của model (lấy ở trang tài liệu của nhà cung cấp). Cột `model` trong `eval/run-N.csv` ghi đúng mã đó. Khi tính chi phí, tra đúng dòng trong bảng giá: tên hiển thị có thể khác mã API, và có model có nhiều dòng giá kèm ngày áp dụng.
- `.env` đã có trong `.gitignore`: **không commit**.

Windows: mở `.env` bằng Notepad (`notepad .env`). Khi lưu, Notepad có thể tự thêm đuôi thành `.env.txt`: ở hộp "Save as type" chọn **All files**. Kiểm bằng `dir`: phải thấy đúng tên `.env`.

## 3. Khung adapter chung — chép vào `codebase/ai.py`

Giữ nguyên docstring, hàm `load_env` và nhánh `fake`. Thêm dòng `import` lên đầu file, dán hàm `post_json`, rồi **thay phần thân sau nhánh fake** của `call_model` bằng đoạn dưới. `@model_call` giữ nguyên: nó tự ghi mỗi lần gọi vào trace và cộng token.

```python
import json
import urllib.error
import urllib.request

SHOW_RAW = False   # đổi thành True để in nguyên phản hồi của API (dùng khi tìm tên trường)


def post_json(url, headers, body, timeout=60):
    """Gửi POST JSON, trả về JSON phản hồi. Chỉ dùng thư viện chuẩn (urllib)."""
    if url.startswith("<") or any(k.startswith("<") for k in headers):
        raise RuntimeError("Chưa điền địa chỉ API hoặc tên header: mở tài liệu chính thức của nhà cung cấp")
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), method="POST",
        headers=dict({"Content-Type": "application/json"}, **headers))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError("HTTP %d: %s" % (e.code, e.read().decode("utf-8", "replace")[:300]))
    if SHOW_RAW:
        print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])
    return data


@model_call
def call_model(system: str, user: str) -> dict:
    if MODEL_PROVIDER == "fake":
        ...                                   # giữ nguyên nhánh fake của khung
    if MODEL_PROVIDER == "gemini":
        r = call_gemini(system, user)         # mục 4.1
    elif MODEL_PROVIDER == "openai":
        r = call_openai(system, user)         # mục 4.2
    elif MODEL_PROVIDER == "anthropic":
        r = call_claude(system, user)         # mục 4.3
    elif MODEL_PROVIDER == "ollama":
        r = call_ollama(system, user)         # mục 4.4
    else:
        raise RuntimeError("MODEL_PROVIDER trong .env chưa đúng: %r" % MODEL_PROVIDER)
    return {"text": r["text"], "model": MODEL_NAME,
            "tokens_in": int(r["tokens_in"]), "tokens_out": int(r["tokens_out"])}
```

- Mỗi lần `call_model` = **một** lần gọi API. Luồng trong `agent.py` gọi model nhiều lần (vd một lần phân loại, một lần trả lời) thì khung tự cộng token của mọi lần — không cần cộng tay.
- Chỉ cần chép **một** hàm `call_…` ở mục 4 (đúng nhà cung cấp nhóm chọn); các nhánh `elif` còn lại không chạy tới nên không sao.

## 4. Bốn ví dụ `call_…`

Ví dụ 4.2–4.4 đã chạy với key thật ngày 25/11/2026: chép nguyên hàm vào `ai.py` là chạy. Ví dụ 4.1 (Gemini) còn chỗ ghi `<xem tài liệu chính thức>`: nhóm điền theo tài liệu chính thức của Google; `post_json` báo "Chưa điền" cho tới khi nhóm thay. Nhà cung cấp đổi API thì làm theo mục 4.0.

Cách nhanh nhất để điền: mở trang "quickstart" của nhà cung cấp, tìm ví dụ gọi bằng REST / curl (không phải SDK), chép địa chỉ, tên header, tên trường. Sau đó bật `SHOW_RAW = True`, chạy `python run.py`, hỏi 1 câu: phản hồi in ra cho thấy câu trả lời nằm ở trường nào.

### 4.0 Đường nhanh: chép ví dụ quickstart chính thức

Không muốn điền từng chỗ trong 4.1–4.4 thì đi đường này:

1. Mở trang quickstart / "get started" của nhà cung cấp đã chọn (trang chính thức, không lấy từ blog).
2. Chép nguyên ví dụ Python **ngắn nhất** gọi được 1 câu. Bản dùng SDK (thư viện của hãng) hay bản REST đều được. Dùng SDK thì ghi tên gói vào `requirements.txt` và ghi lệnh `python -m pip install -r requirements.txt` vào README của nhóm, để giám khảo cài lại được.
3. Dán đoạn đó vào hàm `call_provider(system, user)` dưới đây, rồi trong `call_model` gọi `r = call_provider(system, user)` thay cho khối `if / elif`.
4. In nguyên phản hồi ra **một lần** để tìm chỗ chứa câu trả lời và chỗ chứa số token. Tên trường token của từng hãng: mục 3 của `further-reading/model-prices.md` (repo đề).
5. Trả về đúng dict `{"text": ..., "tokens_in": ..., "tokens_out": ...}`.

| Lấy gì từ trang quickstart | Ghi vào đâu trong `ai.py` |
|---|---|
| Địa chỉ API (bản REST) hoặc tên gói SDK | REST: biến địa chỉ (như `URL_GEMINI`) · SDK: dòng `import` đầu file + `requirements.txt` |
| Cách gửi key (tên header, hoặc tham số khi tạo client) | REST: tham số `headers` của `post_json` · SDK: chỗ `# 1.` dưới đây, dùng biến `API_KEY` |
| Tên model khi gọi API | Dòng `MODEL_NAME=` trong `.env` |
| Trường chứa câu trả lời (và trường token) | Chỗ `# 3.` dưới đây (hoặc hàm `…_text` ở 4.1–4.4) |

```python
def call_provider(system, user):
    """Gọi đúng MỘT lần model. Trả về {"text": str, "tokens_in": int, "tokens_out": int}."""
    # 1. tạo client bằng API_KEY (chép từ quickstart)
    # 2. gửi system + user, model = MODEL_NAME (chép từ quickstart)
    # 3. lấy chữ trả lời + số token từ phản hồi
    raise RuntimeError("Chưa điền: chép ví dụ quickstart vào call_provider()")
    return {"text": text, "tokens_in": tokens_in, "tokens_out": tokens_out}
```

Đường nào cũng được, miễn `python run.py` hỏi 1 câu ra câu trả lời thật và `tokens_in`, `tokens_out` là số lấy từ phản hồi.

### 4.1 Gemini (gói miễn phí)

> Ví dụ này cần nhóm **điền 2 chỗ** theo tài liệu chính thức của Gemini API: địa chỉ API và trường chứa câu trả lời (bảng dưới). Mở tài liệu chính thức để đối chiếu tên trường. Không muốn điền thì đi đường nhanh ở mục 4.0.

| Đã có từ nguồn | Nhóm tự điền |
|---|---|
| Lấy key trong Google AI Studio. Header gửi key: `x-goog-api-key` (ví dụ REST trên trang token của Gemini) | Địa chỉ API để **tạo câu trả lời** (trang token chỉ có địa chỉ đếm token, không có địa chỉ này) |
| Tham số `model`, `input` (theo ví dụ SDK `client.interactions.create(model=..., input=...)` trên trang token) | Trường chứa chữ trả lời trong phản hồi |
| **Token:** trong `usage` của phản hồi: `total_input_tokens` (vào), `total_output_tokens` (ra), `total_thought_tokens` (suy nghĩ — trang giá tính vào giá **ra**) | |

```python
URL_GEMINI = "<xem tài liệu chính thức>"


def gemini_text(data):
    raise RuntimeError("Chưa điền: câu trả lời nằm ở trường nào (bật SHOW_RAW = True để xem)")


def call_gemini(system, user):
    data = post_json(URL_GEMINI, {"x-goog-api-key": API_KEY},
                     {"model": MODEL_NAME, "input": system + "\n\n" + user})
    u = data["usage"]
    return {"text": gemini_text(data),
            "tokens_in": u["total_input_tokens"],
            "tokens_out": u["total_output_tokens"] + u.get("total_thought_tokens", 0)}
```

Gộp `system` vào đầu `input` là cách đơn giản nhất; tài liệu có trường riêng cho hướng dẫn hệ thống thì dùng trường đó.

### 4.2 OpenAI (tài khoản trả tiền)

> **Đã chạy thử** 25/11/2026: `MODEL_NAME=gpt-5.4-nano`, 20 câu, 0 lỗi, ~1,6 giây/câu. Dùng API **Chat Completions**. Token suy luận đã tính trong token ra.

```python
URL_OPENAI = "https://api.openai.com/v1/chat/completions"


def call_openai(system, user):
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    data = post_json(URL_OPENAI, {"Authorization": "Bearer " + API_KEY},
                     {"model": MODEL_NAME, "messages": messages})
    u = data["usage"]
    return {"text": data["choices"][0]["message"]["content"],
            "tokens_in": u["prompt_tokens"], "tokens_out": u["completion_tokens"]}
```

DeepSeek: trang giá DeepSeek ghi có địa chỉ gốc theo định dạng OpenAI (`https://api.deepseek.com`), tên model `deepseek-flash`. Nhóm dùng DeepSeek có thể dùng lại hàm này, đổi `URL_OPENAI` theo tài liệu DeepSeek.

### 4.3 Claude (credit dùng thử Anthropic hoặc tài khoản nhóm)

> **Đã chạy thử** 25/11/2026: `MODEL_NAME=claude-haiku-5-5`, 20 câu, 0 lỗi, 1–2 giây/câu.

- Mã model khi gọi API (ghi vào `MODEL_NAME`) khác tên hiển thị trong bảng giá. Ví dụ "Claude Haiku 5.5" có mã `claude-haiku-5-5`; mã của model khác tra trong tài liệu model của Anthropic.
- Model Claude mới dùng bộ tách token mới, ra khoảng **30% token nhiều hơn** cho cùng đoạn văn (theo trang giá Anthropic). Vì vậy luôn dùng token đo thật. Trên bộ thử của BTC, cùng câu hỏi thì Claude tính ~460 token vào, model khác ~260.

```python
URL_CLAUDE = "https://api.anthropic.com/v1/messages"


def call_claude(system, user):
    data = post_json(URL_CLAUDE,
                     {"x-api-key": API_KEY, "anthropic-version": "2023-06-01"},
                     {"model": MODEL_NAME, "max_tokens": 1024, "system": system or "",
                      "messages": [{"role": "user", "content": user}]})
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    u = data["usage"]
    return {"text": text, "tokens_in": u["input_tokens"], "tokens_out": u["output_tokens"]}
```

`max_tokens` là số token ra tối đa mỗi lần gọi (bắt buộc với API này). Câu trả lời bị cụt thì tăng số này.

Khi tra giá: dùng tên hiển thị trong bảng giá (ví dụ "Claude Haiku 5.5") ở `cost/personas.yaml`, dù `MODEL_NAME` là mã API.

### 4.4 Model chạy trên máy (Ollama + Gemma 4)

> **Đã chạy thử** 25/11/2026 với Ollama 0.40: `MODEL_NAME=gemma4:12b` (đúng, nhưng 43–165 giây/câu) và `MODEL_NAME=llama3.2:3b` (~4 giây/câu). Đọc lưu ý về tốc độ ở mục 1.

- Không cần key: để trống `API_KEY`.
- Cài Ollama và tải model theo trang ollama.com. Ví dụ `ollama pull gemma4:e2b`, bản nhỏ nhất của Gemma 4, nặng 4,6–7,5 GB. Ollama phải đang chạy thì mới gọi được.
- Token: Ollama trả `prompt_eval_count` (vào) và `eval_count` (ra).

```python
URL_OLLAMA = "http://localhost:11434/api/chat"


def call_ollama(system, user):
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    data = post_json(URL_OLLAMA, {}, {"model": MODEL_NAME, "messages": messages, "stream": False}, timeout=300)
    return {"text": data["message"]["content"],
            "tokens_in": data.get("prompt_eval_count", 0), "tokens_out": data.get("eval_count", 0)}
```

Model chạy trên máy không có giá API. Chi phí vẫn phải tính theo **model định dùng khi ra sản phẩm thật** (mục 7). Phản hồi không có số token thì đo token bằng một model thuộc gói miễn phí — token đều = 0 thì `run.py eval` coi là "chưa gọi model thật" và không tính lượt.

## 5. Thử 1 câu rồi chạy bộ câu thử

1. `python run.py` → gõ 1 câu → thấy câu trả lời của model và dòng `(model: … · token vào … / ra …)` là đã nối được (Ctrl+C để thoát).
2. `python run.py eval --try` → chạy 3 câu thử đầu (`--try 5` = 5 câu) → màn hình in `token vào` > 0 cho từng câu và dòng "Nối model được". Lượt thử ghi vào `eval/run-try.csv` (ghi đè mỗi lần), không chiếm số `run-1` — không phải xoá gì.
3. Lỗi "Chưa điền …": còn chỗ `<xem tài liệu chính thức>` hoặc hàm `raise RuntimeError("Chưa điền …")` chưa thay.
4. `python run.py eval` → `eval/run-1.csv` + `traces/run-1.jsonl`. Model còn giả hoặc token đều = 0: bộ chạy chỉ ghi `eval/run-mock.csv`, không tính lượt. **Mọi** câu đều lỗi: ghi `eval/run-error.csv`, không tính lượt — sửa rồi chạy lại, số lượt không bị "mất".
5. Tắt `SHOW_RAW` (đặt lại `False`) trước khi chạy bộ câu thử cho gọn.

Gõ `python`, `python3` hay `py`: xem mục "Chạy trong 3 phút" của `README.md`.

## 6. Lỗi hay gặp

| Triệu chứng | Nguyên nhân hay gặp | Cách xử lý |
|---|---|---|
| `HTTP 401` / `HTTP 403` | Sai key, key chưa bật cho API này, `.env` chưa lưu | Mở `.env` xem key (không thừa dấu cách, không dấu ngoặc kép); tạo key mới nếu cần |
| `HTTP 429`, hoặc chạy được vài câu rồi lỗi hàng loạt | Hết lượt gói miễn phí (giới hạn số lượt / phút hoặc / ngày) | Chạy bộ câu thử và mô phỏng **sớm**, đừng để sát mốc. Giãn cách: `python run.py eval --wait 4` (cũng dùng được cho `simulate`). Hết lượt trong ngày: dùng project / key khác của thành viên khác, ghi rõ trong báo cáo |
| Lượt có một số câu lỗi kỹ thuật (cột `error` có chữ) | Hết lượt, mất mạng giữa chừng | **Không sửa tay file đó.** Chạy lại `python run.py eval` → lượt mới (`run-2.csv`…). Ghi mọi lượt vào bảng ở `eval/README.md` mục 5 (lượt nào chạy lại, vì sao); không xoá file lượt nào |
| `HTTP 400` | Sai tên trường trong thân yêu cầu hoặc sai tên model | Đối chiếu ví dụ REST của tài liệu; `MODEL_NAME` đúng tên model API |
| `HTTP 400` kèm "credit balance is too low" (hoặc lời báo hết tiền / hết hạn mức tương tự) | Tài khoản hết credit. Key vẫn đúng, chỉ là hết tiền | Nạp credit, hoặc dùng key của thành viên khác / nhà cung cấp khác. Ghi rõ đổi gì trong `eval/README.md` |
| `ConnectionRefusedError` / `URLError` khi dùng Ollama | Ollama chưa chạy, hoặc chưa tải model | Mở Ollama (hoặc chạy `ollama serve`), `ollama pull <model>`, kiểm bằng `ollama list` |
| `TimeoutError` / `URLError` | Mạng chậm, model trên máy chạy lâu | Tăng `timeout` trong `post_json`; thử lại; model trên máy: dùng bản nhỏ hơn |
| `KeyError: 'usage'` hoặc tên trường token | Phản hồi không có trường đó (API khác phiên bản, hoặc phản hồi là thông báo lỗi) | Bật `SHOW_RAW = True`, xem phản hồi thật, sửa tên trường |
| Model trả về rỗng | Bị bộ lọc an toàn chặn, hoặc hết số token ra tối đa (nhất là model có suy nghĩ) | Xem phản hồi thật; tăng số token ra tối đa; ghi câu thử đó vào báo cáo như một lỗi |
| Cột `error`: "Hợp đồng call_model(): thiếu khoá… / phải là số nguyên…" | `call_model` trả thiếu khoá hoặc token không phải số nguyên | Trả đúng 4 khoá `text`, `model`, `tokens_in`, `tokens_out`; ép `int(...)` cho token |
| Cột `error`: "answer() phải trả dict có khoá output" | `answer()` trong `agent.py` trả sai dạng | Trả `{"output": "<chuỗi>"}` |
| `eval` báo "chưa gọi model thật" | `.env` chưa có `MODEL_PROVIDER` (đang chế độ giả), hoặc token đều = 0 | Điền `.env` (mục 2), lấy token từ `usage` của phản hồi; thử bằng `python run.py eval --try` |
| `score` báo "CHƯA ĐỦ BỘ" | File lượt thiếu câu so với `eval/benchmark.csv` (lượt bị dừng giữa chừng, hoặc nhóm thêm câu sau khi chạy) | Chạy lại `python run.py eval` để có lượt đủ cả bộ. Bấm Ctrl+C giữa lượt thì bộ chạy chỉ ghi `eval/run-stopped.csv` |

Lộ key (lỡ commit `.env`, dán key lên kênh chung): **thu hồi key ngay** trên trang nhà cung cấp rồi mới xoá khỏi repo — xoá file không đủ, key cũ coi như đã lộ.

## 7. Đo trên model X, tính giá model Y

Chi phí là **ước tính** từ token đo được khi chạy `python run.py simulate`. Nhóm có thể đo token bằng model thuộc gói miễn phí rồi tính giá của model định dùng thật (≥2 mức model, khai trong `cost/personas.yaml` mục `prices`). Ghi rõ một câu trong `cost/cost-estimate.md`: "đo token trên model X, tính giá model Y". Nói rõ giới hạn: số token giữa hai model của hai hãng có thể lệch nhau, vì mỗi hãng tách token khác nhau.

Tiếng Việt: không có quy tắc quy đổi chữ → token chính thức. **Bắt buộc đo thật**, không quy đổi từ số chữ.
