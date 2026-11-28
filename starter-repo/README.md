# 4thangtay — Trợ lý giải thích 8 chỉ số CBC thai kỳ (Track F)

Tích hợp phần AI đọc phiếu với 8 mã `HGB, RBC, HCT, MCV, MCH, MCHC, WBC, PLT`; tham khảo [hướng dẫn dùng app](docs/cbc-ai-handoff.md).

Backend FastAPI cho Railway: [triển khai và SQLite volume](docs/railway-deployment.md). Giao diện frontend Vercel: [hợp đồng API, ví dụ fetch và ghi âm](docs/frontend-api-handoff.md).

Đọc phạm vi và cách đánh giá an toàn: [Độ tin cậy và xử lý khi kết quả có thể sai](docs/quality-and-safety.md). Tỷ lệ trong benchmark là tỷ lệ đạt trên bộ câu cố định, không phải độ chính xác lâm sàng.

**Chạy ứng dụng web local (Next.js + FastAPI):** xem [hướng dẫn chạy local](docs/local-development.md). Chạy riêng `start-voice-demo.ps1` chỉ mở màn hình Streamlit thử mic cũ ở cổng 8501; đó không phải web app đầy đủ.

**Thành viên, lớp, track:** xem [TEAMS.md](TEAMS.md). **Điền TEAMS.md đúng format**: khi chấm và đánh giá, BTC quét file này để ghép điểm cho từng người.

*Lát cắt = phần nhỏ nhất làm xong được trong hackathon: một người dùng · một việc · một quyết định AI · một kết quả.*

---

## Nhóm làm gì, khung làm gì

| Nhóm quyết định và viết | Khung làm sẵn (không cần sửa) |
|---|---|
| Người dùng, pain, bằng chứng, impact (`evidence/`, `spec.md` §1–§2) | — |
| Hình dạng giải pháp, công cụ, prompt, luồng (`spec.md` §4, `codebase/agent.py`, `tools.py`, `ai.py`) | Ghi mọi lần gọi model / công cụ vào trace, cộng token (`codebase/tracing.py`) |
| Bộ câu thử, metric, chuẩn "đạt" (`eval/benchmark.csv`, `eval/metric_spec.yaml`, `spec.md` §7) | Kiểm đủ cột, đủ câu `kho` / `tu_choi`, đủ ≥1/3 câu từ người dùng / data thật (`run.py check`) |
| Chấm cột `pass` theo metric spec | Chạy cả bộ một lệnh, có run ID, model, token từng câu (`run.py eval`) · tính % đạt (`run.py score`) |
| Persona, số người dùng thật, giá model (`cost/personas.yaml`) | Sinh ~50 phiên, chạy thật qua bản chạy thử, tính chi phí / phiên, / task thành công, / tháng 3 kịch bản (`run.py simulate`) |

## Chạy trong 3 phút

Bộ khung cần **Python 3.10 trở lên**. **Không cần `pip install` cho CLI cốt lõi (`run.py`).**

**Bước 1 — Mở cửa sổ lệnh ngay trong thư mục repo (`starter-repo/`)**

| Windows (PowerShell) | macOS |
|---|---|
| Mở thư mục repo bằng File Explorer → bấm vào thanh địa chỉ → gõ `powershell` → Enter | Mở **Terminal** → `cd <duong-dan-repo>` → Enter |

**Bước 2 — Kiểm Python và chạy thử**

| Việc | Windows (PowerShell) | macOS / Linux |
|---|---|---|
| Kiểm Python | `python --version` (hoặc `py --version`) | `python3 --version` |
| Chạy bản chạy thử (chế độ giả CP2) | `python run.py` | `python3 run.py` |
| Kiểm bộ câu thử & `TEAMS.md` | `python run.py check` | `python3 run.py check` |
| Tạo file `.env` để nối model (CP3) | `copy .env.example .env` | `cp .env.example .env` |

## Lệnh

| Lệnh | Làm gì |
|---|---|
| `python run.py` | Chạy bản chạy thử (gõ đầu vào JSON gồm `report` và `question`, nhận kết quả kèm token/tool count) |
| `python run.py check` | Kiểm `eval/benchmark.csv`, `eval/metric_spec.yaml` và `TEAMS.md`. Chỉ cảnh báo, không sửa file |
| `python run.py eval --try` | **Thử nối model:** chạy 3 câu đầu → `eval/run-try.csv` |
| `python run.py eval` | Chạy cả bộ qua `codebase/agent.py` → `eval/run-1.csv` + `traces/run-1.jsonl` |
| `python run.py score eval/run-1.csv` | Sau khi điền cột `pass` (1 / 0): in % đạt tổng và theo `type` |
| `python run.py simulate --try` | Thử mô phỏng chi phí 10 phiên → `cost/simulate-try.csv` |
| `python run.py simulate` | Mô phỏng chi phí khi dùng thật theo `cost/personas.yaml` (≥50 phiên) → `cost/simulate-N.csv` + `cost/simulate-N-summary.md` |

## Bản chạy thử — viết ở đâu

| File | Viết gì | Bước guide |
|---|---|---|
| `codebase/agent.py` | `answer(text)` — luồng workflow cố định, cổng chặn khẩn cấp & đối chiếu trước khi gọi LLM | 3.2 |
| `codebase/tools.py` | `compare_cbc(report)` — chuẩn hóa đơn vị bằng `Decimal` và đối chiếu khoảng `lab`/`study` (`@tool`) | 2.2, 3.2 |
| `codebase/references.py` & `reference_data.py` | Kiểm tra tuổi thai `XwYd` và tra cứu bảng khoảng tham chiếu *Pham et al. (2023)* | 2.2, 3.2 |
| `codebase/ai.py` | `call_model(system, user)` — chỗ duy nhất gọi model (`fake` cho CP2; `ollama` / `openai_compatible` cho CP3) | 3.3 |

## Phần nào thật, phần nào giả

| Thành phần | Thật / Giả | Ghi chú |
|---|---|---|
| Hàm quy đổi đơn vị & đối chiếu CBC (`compare_cbc`) | **Thật** | Chạy số học `Decimal` chính xác trên 8 mã CBC, kèm bảng khoảng *Pham et al. (2023)* (`study`) và khoảng trên phiếu (`lab`) |
| Cổng chặn an toàn (`urgent`, `out_of_scope`, `needs_input`) | **Thật** | Chặn tình huống khẩn cấp, ngoài đối tượng thai phụ trưởng thành, thiếu đơn vị/khoảng, sai tuổi thai |
| Lời gọi AI phân loại ý định/chỉ số (`call_model`) | **Chế độ giả ở CP2** → **Thật ở CP3** | CP2 chạy chế độ `fake` có nhãn `[AI giả]` để đi trọn luồng; đã cài sẵn kết nối Ollama / OpenAI-compatible trong `codebase/ai.py` |
| Bộ 3 phiếu xét nghiệm mẫu (`data/cbc-mock-01..03.*`) | **Giả lập (`synthetic`)** | Tự dựng từ kịch bản lâm sàng cố định, gắn watermark rõ ràng, không dùng phiếu thật của bệnh nhân |

## Dùng AI vào việc gì

Nhóm sử dụng trợ lý lập trình AI (Codex / Antigravity) để hỗ trợ dựng khung code đối chiếu CBC, unit test, tạo mẫu HTML phiếu giả lập `synthetic`, và rà cấu trúc tài liệu Markdown (`spec.md`, `canvas.md`, `DATA_CARD.md`). Toàn bộ số liệu từ *Pham et al. (2023)* (`416/837`, `95/837`), quy tắc an toàn y khoa, quy đổi `Decimal` và tiêu chí chấm được thành viên nhóm tự kiểm tra đối chiếu với nguồn gốc; nhóm không dùng AI để bịa phỏng vấn hay sửa kết quả chạy đánh giá. Chi tiết: [docs/ai-usage.md](docs/ai-usage.md), quy ước coding agent: [AGENTS.md](AGENTS.md).

## Bảy hạng mục bắt buộc — nằm ở file nào

| # | Hạng mục | File |
|---|---|---|
| 1 | Bằng chứng pain | `evidence/` (tổng hợp ở `evidence/summary.md`, `evidence/data-mining.md`, `evidence/interviews/PLAN.md`) |
| 2 | Impact có số | `spec.md` §2 |
| 3 | Thiết kế giải pháp | `spec.md` §4–§6 |
| 4 | Bản chạy thử làm trọn lát cắt | `codebase/` · lệnh `python run.py` |
| 5 | Định nghĩa "tốt" + bộ câu thử | `data/DATA_CARD.md` · `eval/benchmark.csv` · `eval/metric_spec.yaml` · `eval/README.md` |
| 6 | Mô phỏng chi phí khi dùng thật | `cost/` |
| 7 | Slide + demo + video dự phòng | `demo-slides.pdf` ở thư mục gốc · link video: *(cập nhật ở CP3/CP4)* |
| + | *Bonus:* người dùng thử | `validation/log.md` |
