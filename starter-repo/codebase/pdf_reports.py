"""Render a small report PDF into bounded page images without saving uploads."""
import io
import math

MAX_PDF_BYTES = 10 * 1024 * 1024
MAX_PDF_PAGES = 3
MAX_PAGE_EDGE = 2000


def render_pdf(content: bytes) -> list[bytes]:
    if not isinstance(content, bytes) or not content.startswith(b"%PDF-") or len(content) > MAX_PDF_BYTES:
        raise ValueError("Chọn PDF hợp lệ, tối đa 10 MB.")
    try:
        import pypdfium2 as pdfium
    except (ImportError, OSError):
        raise RuntimeError("Máy chủ chưa nạp được thư viện đọc PDF. Cài requirements-api.txt rồi khởi động lại.") from None
    try:
        document = pdfium.PdfDocument(content)
    except pdfium.PdfiumError:
        raise ValueError("Không mở được PDF. Chị dùng tệp không đặt mật khẩu, hoặc tải ảnh JPG/PNG của phiếu.") from None
    images = []
    try:
        if not 1 <= len(document) <= MAX_PDF_PAGES:
            raise ValueError("PDF chỉ nhận từ một đến ba trang. Chị tách riêng các trang của một phiếu CBC rồi tải lại.")
        for index in range(len(document)):
            page = document[index]
            try:
                width, height = page.get_size()
                if not all(math.isfinite(n) and 0 < n <= 20000 for n in (width, height)):
                    raise ValueError("Kích thước trang PDF không hợp lệ.")
                bitmap = page.render(scale=min(2, MAX_PAGE_EDGE / max(width, height)))
                try:
                    with bitmap.to_pil() as image:
                        output = io.BytesIO()
                        image.save(output, format="PNG")
                        images.append(output.getvalue())
                finally:
                    bitmap.close()
            finally:
                page.close()
    except pdfium.PdfiumError:
        raise ValueError("Không đọc được một trang PDF. Chị thử bản PDF khác hoặc ảnh rõ của phiếu.") from None
    finally:
        document.close()
    return images
