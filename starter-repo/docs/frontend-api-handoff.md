# Bàn giao frontend Vercel

Backend FastAPI hỗ trợ 8 chỉ số CBC đề xuất (HGB, RBC, HCT, MCV, MCH, MCHC, WBC, PLT), SQLite, Zipformer và VieNeu API. Frontend React/Next.js gọi URL Railway bằng HTTPS. Toàn bộ đường dẫn dưới đây tính từ gốc URL backend.

## Chạy và kết nối

Backend local dùng Python 3.12:

```sh
pip install -r requirements-api.txt
cp .env.example .env
python -m codebase.serve
```

Điền APP_USERNAME, APP_PASSWORD, APP_SECRET trong .env. APP_SECRET là chuỗi ngẫu nhiên ít nhất 32 ký tự. Zipformer cần ZIPFORMER_BACKEND=onnx và ZIPFORMER_MODEL_DIR trỏ đến model đã giải nén. Chọn MODEL_PROVIDER=fake để thử luồng nhập tay và hỏi đáp giả. Ảnh và giọng đọc cần cấu hình nhà cung cấp thật.

OpenAPI và màn hình thử nằm ở `/openapi.json` và `/docs`. Trong Vercel đặt:

```dotenv
NEXT_PUBLIC_CBC_API_URL=https://your-backend.up.railway.app
```

Railway đặt CORS_ORIGINS bằng origin Vercel chính xác, ví dụ https://your-app.vercel.app. Thêm localhost khi phát triển. Các khóa AI, mật khẩu app và APP_SECRET được giữ trên backend.

## Endpoint

Ngoài health, login và OpenAPI, mỗi yêu cầu gửi header `Authorization: Bearer <access_token>`.

| Method | Path | Đầu vào | Đầu ra |
|---|---|---|---|
| GET | /health | — | status |
| POST | /v1/auth/login | username, password | access_token, token_type, expires_in |
| GET | /v1/catalog | — | Mảng 8 mục code, name, unit, group |
| GET | /v1/references?gestational_age=21w3d | Tuổi thai | reference_mode, trimester, gestational_age, source, note, rows khoảng nghiên cứu |
| POST | /v1/reports/validate | Report | status, rows hoặc issues |
| POST | /v1/reports/extract | Multipart field file, JPG/PNG | rows, warnings của bản nháp |
| POST | /v1/sessions | — | session_id, revision=0, report=null |
| GET | /v1/sessions/{id} | — | Phiếu đã xác nhận và revision |
| PUT | /v1/sessions/{id}/report | report, confirmed=true, expected_revision | session_id, revision, report, analysis |
| POST | /v1/sessions/{id}/invalidate | expected_revision | Trạng thái phiên mới với report=null |
| GET | /v1/sessions/{id}/analysis?expected_revision=N | revision đang hiển thị | analysis |
| GET | /v1/sessions/{id}/history | — | messages |
| POST | /v1/sessions/{id}/chat | question, expected_revision, request_id | status, output, các trường kết quả, usage và revision |
| DELETE | /v1/sessions/{id} | — | 204 |
| POST | /v1/speech/transcribe | Multipart field file, WAV | text |
| POST | /v1/speech/synthesize | text | WAV binary, Content-Type audio/wav |

Luồng mới mặc định dùng `reference_mode: "study"`: người dùng nhập kết quả và đơn vị, backend chọn khoảng nghiên cứu theo tuổi thai. Payload tối thiểu dùng chung cho nhập tay và dữ liệu đọc ảnh:

```json
{
  "adult_confirmed": true,
  "pregnancy_status": "pregnant",
  "gestational_age": "21w3d",
  "reference_mode": "study",
  "rows": [
    {
      "analyte": "HGB",
      "value": "108",
      "unit": "g/L"
    }
  ]
}
```

Lấy danh mục và đơn vị gợi ý từ /v1/catalog. Chỉ gửi các chỉ số trong 8 mã hỗ trợ, từ 1 đến 8 dòng. Giá trị và đơn vị phải được người dùng kiểm lại; giữ null hoặc trống nếu chưa đọc được, không tự điền đơn vị bị thiếu từ OCR. Tuổi thai lúc xét nghiệm, xác nhận từ 18 tuổi và tình trạng đang mang thai vẫn bắt buộc để đối chiếu. Gửi validate để hiện những trường cần sửa. Mẫu đủ 24 chỉ số nằm ở [full-panel-demo.json](../data/full-panel-demo.json); lấy các dòng trong 8 mã hỗ trợ, số và khoảng là dữ liệu dựng.

Frontend có thể gọi `/v1/references?gestational_age=21w3d` để xem trước khoảng theo tuổi thai. Phản hồi gồm `reference_mode: "study"`, `trimester` (1/2/3), `gestational_age`, `source` (title/url), `note` và `rows` chứa analyte/unit/ref_low/ref_high. Không dùng dữ liệu xem trước để tự tính trạng thái; bảng và kết luận hiển thị lấy từ validate/analysis. Quy ước của demo giữ 28w6d trong tam cá nguyệt 2, từ 29w0d sang tam cá nguyệt 3.

Chế độ `reference_mode: "lab"` vẫn dùng các khoảng do người dùng xác nhận trên phiếu: mỗi dòng thêm `ref_low`, `ref_high`, `ref_unit`, ví dụ `"ref_low": "110", "ref_high": "140", "ref_unit": "g/L"` cho dòng HGB trên. Chọn một nguồn cho toàn phiếu. Explicit study bỏ qua mọi khoảng gửi kèm, kể cả khoảng OCR. Để tương thích dữ liệu cũ, khi thiếu reference_mode: không có khoảng nào thì dùng study, có bất kỳ khoảng nào thì giữ lab và yêu cầu bổ sung đủ; không tự trộn nguồn hay đổi phiếu cũ sang study.

Kết quả đối chiếu và analysis thêm `reference_mode`, `trimester`, `reference_source` và `reference_note`. Nguồn có `title`; `url` là tùy chọn và có thể vắng trong lab vì nguồn là phiếu của người dùng. Hiện note và tên nguồn cùng bảng kết quả, kể cả bản tải xuống; chỉ tạo liên kết khi có url. Ở study, tiêu đề cột là “Khoảng nghiên cứu theo tam cá nguyệt”; ở lab là “Khoảng trên phiếu”. Khoảng công bố từ Pham et al. (2023) phục vụ đối chiếu nghiên cứu, không phải ngưỡng chẩn đoán hoặc khoảng đã được xác nhận cho phòng xét nghiệm của người dùng. Hiện nguyên reference_note để người dùng thấy giới hạn quần thể, tiêu chí tuyển chọn và khác biệt phương pháp/thiết bị áp dụng.

Mẫu có trường `notice` chỉ để hiển thị. Trước khi gửi API, lấy đúng các trường Report, ví dụ `const { notice, ...report } = sample;`. API từ chối khóa ngoài schema để phát hiện lỗi tích hợp.

## Thứ tự luồng người dùng

1. Login lấy bearer token, có hạn một giờ. Giữ token trong bộ nhớ phiên frontend và xóa khi logout hoặc nhận 401. Đây là tài khoản demo chung của nhóm; các phiên được nhận diện bằng mã ngẫu nhiên.
2. Tạo session và giữ session_id cùng revision. Có thể cho người dùng giữ mã phiên để mở lại qua GET sau khi login.
3. Chọn study mặc định, nhập từng kết quả/đơn vị và tuổi thai, hoặc đọc ảnh qua extract. Ảnh gửi đến dịch vụ AI đã cấu hình, vì vậy giao diện cho biết thao tác này trước nút đọc ảnh. Kết quả extract vẫn có ref_low/ref_high/ref_unit/warnings nhưng là bản nháp cần kiểm lại; study chỉ dùng analyte/value/unit và bỏ các khoảng OCR. Người dùng muốn khoảng trên phiếu chọn lab rõ ràng và kiểm cả khoảng.
4. Khi người dùng xác nhận các trường, PUT report kèm revision đang xem. Hiện analysis ngay, gồm rows, counts, output, sources và metadata nguồn khoảng. rows có trạng thái below/within/above theo nguồn đã chọn; dùng nhãn khoảng nghiên cứu hoặc khoảng trên phiếu tương ứng, không diễn đạt thành chẩn đoán.
5. Khi sửa kết quả, đơn vị, tuổi thai, nguồn khoảng hoặc thay phiếu, dừng cho hỏi trên kết quả cũ và gọi invalidate với revision hiện tại. Cập nhật revision từ phản hồi, xóa kết quả/câu hỏi/bản ghi âm cũ ở frontend. Xác nhận lại trước khi hỏi tiếp.
6. Gửi câu hỏi qua chat. Mỗi lần bấm gửi tạo request_id bằng crypto.randomUUID(), giữ cùng ID và revision khi thử lại cùng yêu cầu. Khi đổi câu hỏi dùng ID mới.
7. Hiện output trước, sau đó nếu người dùng bật giọng đọc thì gửi output tới synthesize và phát WAV nhận về. Tổng hợp giọng đọc là một lời gọi API có thể phát sinh phí, nên chỉ gọi khi người dùng yêu cầu.

GET history trả câu hỏi, result và thời điểm đã lưu cho phiếu hiện tại. Âm thanh và ảnh chưa được lưu vào DB. Khi gọi DELETE, phiên và lịch sử được xóa. Lần xác nhận phiếu khác hoặc invalidate xóa lịch sử gắn với phiếu trước trong cùng phiên.

Frontend cần gắn mỗi tác vụ với session, revision và phiên bản bản nháp lúc bắt đầu. Khi người dùng sửa phiếu, hủy request đang chờ bằng AbortController và bỏ mọi phản hồi về muộn thuộc bản nháp/revision cũ, gồm ảnh, phân tích, chat và audio. Phản hồi PUT là snapshot tại thời điểm ghi; GET mới nhất có thể đã chuyển revision nếu một tab khác vừa sửa phiếu. Hủy fetch không bảo đảm hủy lời gọi có phí đã chạy ở server.

## Ví dụ fetch cho Next.js

```ts
const base = process.env.NEXT_PUBLIC_CBC_API_URL!.replace(/\/$/, "");
let accessToken = "";

async function api(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  if (accessToken) headers.set("Authorization", "Bearer " + accessToken);
  if (init.body && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(base + path, { ...init, headers });
  if (!response.ok) {
    if (response.status === 401) accessToken = "";
    const error = await response.json().catch(() => ({}));
    throw new Error(JSON.stringify({ status: response.status, detail: error.detail }));
  }
  if (response.status === 204) return null;
  if (response.headers.get("Content-Type")?.includes("audio/")) return response.blob();
  return response.json();
}

// username/password là dữ liệu người dùng nhập trong màn hình login.
const login = await api("/v1/auth/login", {
  method: "POST", body: JSON.stringify({ username, password })
});
accessToken = login.access_token;
const session = await api("/v1/sessions", { method: "POST" });
const confirmed = await api("/v1/sessions/" + session.session_id + "/report", {
  method: "PUT",
  body: JSON.stringify({ report, confirmed: true, expected_revision: session.revision })
});
// Hiển thị confirmed.analysis trước khi hỏi tiếp.
const reply = await api("/v1/sessions/" + session.session_id + "/chat", {
  method: "POST",
  body: JSON.stringify({
    question, expected_revision: confirmed.revision, request_id: crypto.randomUUID()
  })
});
const wav = await api("/v1/speech/synthesize", {
  method: "POST", body: JSON.stringify({ text: reply.output })
});
const audioUrl = URL.createObjectURL(wav);
const player = new Audio(audioUrl);
// Nếu trình duyệt chặn autoplay, hiện nút Play cho người dùng.
await player.play();
// URL.revokeObjectURL(audioUrl) khi người dùng bỏ audio hoặc component unmount.
```

Upload dùng FormData và để trình duyệt tự đặt Content-Type cùng multipart boundary:

```ts
const form = new FormData();
form.append("file", imageFile);
const draft = await api("/v1/reports/extract", { method: "POST", body: form });
// Giữ trường thiếu ở trạng thái trống, cho người dùng sửa trước khi xác nhận.
const studyRows = draft.rows.map(({ analyte, value, unit }) => ({ analyte, value, unit }));
// Report mới: { adult_confirmed, pregnancy_status, gestational_age,
//              reference_mode: "study", rows: studyRows }.
```

## Ghi âm WAV 16 kHz trên trình duyệt

Zipformer nhận WAV PCM mono 16-bit, 16 kHz, tối đa 30 giây qua backend ONNX. MediaRecorder thường trả WebM hoặc Ogg; cần giải mã và đổi sang WAV trước khi upload. Hàm dưới nhận blob ghi âm bằng MediaRecorder:

```ts
async function toWav16k(blob: Blob): Promise<Blob> {
  const context = new AudioContext();
  let decoded: AudioBuffer;
  try {
    decoded = await context.decodeAudioData(await blob.arrayBuffer());
  } finally {
    await context.close();
  }
  if (!decoded.duration || decoded.duration > 30) {
    throw new Error("Ghi âm từ trên 0 đến 30 giây.");
  }
  const offline = new OfflineAudioContext(1, Math.ceil(decoded.duration * 16000), 16000);
  const source = offline.createBufferSource();
  source.buffer = decoded;
  source.connect(offline.destination);
  source.start();
  const rendered = await offline.startRendering();
  const samples = rendered.getChannelData(0);
  const bytes = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(bytes);
  const write = (offset: number, value: string) =>
    [...value].forEach((letter, i) => view.setUint8(offset + i, letter.charCodeAt(0)));
  write(0, "RIFF"); view.setUint32(4, bytes.byteLength - 8, true);
  write(8, "WAVE"); write(12, "fmt ");
  view.setUint32(16, 16, true); view.setUint16(20, 1, true);
  view.setUint16(22, 1, true); view.setUint32(24, 16000, true);
  view.setUint32(28, 32000, true); view.setUint16(32, 2, true);
  view.setUint16(34, 16, true); write(36, "data");
  view.setUint32(40, samples.length * 2, true);
  samples.forEach((sample, i) => {
    const value = Math.max(-1, Math.min(1, sample));
    view.setInt16(44 + i * 2, Math.round(value * (value < 0 ? 32768 : 32767)), true);
  });
  return new Blob([bytes], { type: "audio/wav" });
}

const wavForm = new FormData();
wavForm.append("file", await toWav16k(recordedBlob), "question.wav");
const { text } = await api("/v1/speech/transcribe", { method: "POST", body: wavForm });
// Điền text vào ô cho người dùng sửa; gửi câu hỏi đã xác nhận sang chat.
```

## Xử lý lỗi

| HTTP | Xử lý frontend |
|---|---|
| 401 | Xóa token và login lại |
| 404 | Mã phiên không tồn tại hoặc phiên đã bị xóa |
| 409 | Tải lại trạng thái phiên và revision, cho người dùng kiểm tra trước khi gửi lại |
| 413 | Giảm tệp; ảnh tối đa 10 MB, WAV tối đa 3 MB, toàn request tối đa 11 MB |
| 422 | Sửa payload hoặc các trường xét nghiệm theo detail/issues |
| 429 | Một tác vụ model đang chạy, đọc Retry-After và cho thử lại sau |
| 502 | Nhà cung cấp AI/âm thanh hoặc cấu hình chưa đáp ứng; giữ nội dung đã nhập |
| 503 | Backend đang giới hạn kết nối hoặc tài khoản demo server chưa được cấu hình |

Validate có thể trả HTTP 200 với status=needs_input hoặc out_of_scope. Kiểm status trong JSON để hướng dẫn sửa phiếu. Kết quả explained, analyzed, clarify_question, medical_advice, urgent có output hiển thị được. Các lời gọi ảnh và TTS dùng API trả phí nên tránh tự động thử lại khi timeout.

Backend dùng một worker, một khe tác vụ model và tối đa tám kết nối đồng thời. Health và tài liệu API có thể hoạt động khi thiếu khóa dịch vụ; cần thử từng nhà cung cấp bằng dữ liệu giả lập trước buổi demo. Xem [hướng dẫn Railway](railway-deployment.md) để cấu hình volume, biến môi trường và domain.

## Kiểm thử backend khi tích hợp

Từ thư mục `starter-repo`, cài `python -m pip install -r requirements-dev.txt`, rồi chạy `python -m unittest discover -s tests -q`. Bộ kiểm thử HTTP dùng SQLite tạm và giả lập lời gọi API ngoài, không cần API key và không phát sinh phí.
