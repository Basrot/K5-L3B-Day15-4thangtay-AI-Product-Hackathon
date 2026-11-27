"""Đào bài Hỏi - Đáp công khai về xét nghiệm máu CBC đa nguồn (BV Từ Dũ & MEDLATEC).

Chạy tái lập:
  python -u evidence/mine_public_qa.py --tudu-pages 300 --med-spk-pages 53 --med-hh-pages 6
  python evidence/mine_public_qa.py --verify
Chỉ dùng thư viện chuẩn Python; tự động gỡ tên tác giả/PII và không lưu toàn văn HTML vào repo.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import html
import json
from pathlib import Path
import re
import ssl
import sys
import time
import urllib.error
import urllib.request

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SSL_CTX = ssl.create_default_context()
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HackathonStudy/1.0)"}

TUDU_BASE = "https://tudu.com.vn"
TUDU_CAT = "/vn/suc-khoe-mang-thai/"
MED_BASE = "https://medlatec.vn"
MED_SPK_CAT = "/hoi-dap/san-phu-khoa-c11534"
MED_HH_CAT = "/hoi-dap/huyet-hoc-c11541"

# Bộ lọc tầng 1 (danh mục Từ Dũ & lọc bài CBC trên MEDLATEC)
PREFILTER_RE = re.compile(
    r"công thức máu|tổng phân tích tế bào máu|huyết đồ|huyết học|xét nghiệm máu|"
    r"\bhgb\b|\bhb\b|huyết sắc tố|hemoglobin|\brbc\b|hồng cầu|\bhct\b|hematocrit|"
    r"\bmcv\b|\bmch\b|\bmchc\b|\bwbc\b|bạch cầu|\bplt\b|tiểu cầu|thiếu máu|"
    r"thalassemia|tan máu bẩm sinh|\bferritin\b|huyết thanh|máu lắng|viên sắt|bổ sung sắt",
    re.IGNORECASE,
)

# Các xét nghiệm không phải CBC huyết học để tránh nhiễu
EXCLUDE_ONLY_RE = re.compile(
    r"beta\s*hcg|tiểu đường thai kỳ|dung nạp đường|nipt|double test|triple test|"
    r"rubella|viêm gan|giang mai|hiv|zika|đo\s*đ[ộô]\s*mờ\s*da\s*gáy|tụ\s*dịch|"
    r"nang\s*bạch\s*huyết|nhóm\s*máu\s*rh|sốt\s*xuất\s*huyết",
    re.IGNORECASE,
)

STRONG_HEME_RE = re.compile(
    r"công thức máu|tổng phân tích tế bào máu|huyết đồ|\bhgb\b|\bhb\b|huyết sắc tố|hemoglobin|"
    r"\brbc\b|hồng cầu|\bhct\b|hematocrit|\bmcv\b|\bmch\b|\bmchc\b|\bwbc\b|\bplt\b|tiểu cầu|"
    r"thiếu máu|thalassemia|tan máu bẩm sinh|\bferritin\b",
    re.IGNORECASE,
)

PREGNANCY_RE = re.compile(
    r"mang thai|có thai|bầu|thai\s*\d+|song\s*thai|tuần\s*thai|tam cá nguyệt|thai phụ|thai nhi|"
    r"vợ\s*em.*?(?:thai|bầu)|tiền\s*sản|chuẩn bị mang thai|sắp\s*sinh|sau\s*sinh",
    re.IGNORECASE,
)

PHONE_RE = re.compile(r"\b0\d{2,3}[.\s-]?\d{3}[.\s-]?\d{3,4}\b")
LONG_NUM_RE = re.compile(r"\b\d{7,}\b")
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", re.IGNORECASE)
PWD_RE = re.compile(r"(mật\s*khẩu|mã\s*bảo\s*mật|pass(?:word)?)\s*[:=]?\s*\S+", re.IGNORECASE)
NAME_INTRO_RE = re.compile(
    r"\b(em|tôi|mình|cháu)\s+tên\s+(?:là\s+)?([A-ZÀ-Ỹa-zà-ỹĐđ]+(?:\s+[A-ZÀ-Ỹa-zà-ỹĐđ]+){0,3})",
    re.IGNORECASE,
)


def fetch(url: str) -> str:
    last_err = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=10, context=SSL_CTX) as resp:
                return resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            if exc.code in (400, 403, 404, 410):
                raise
            last_err = exc
            time.sleep(0.3 * (attempt + 1))
        except Exception as exc:
            last_err = exc
            time.sleep(0.3 * (attempt + 1))
    raise last_err


def clean_html_text(raw_html: str) -> str:
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw_html, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</div>|</h[1-6]>|</li>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in s.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def scrub_pii(text: str) -> str:
    s = EMAIL_RE.sub("[ẩn email]", text)
    s = PHONE_RE.sub("[ẩn SĐT]", s)
    s = PWD_RE.sub(r"\1 [đã ẩn]", s)
    s = LONG_NUM_RE.sub("[mã XN]", s)
    s = NAME_INTRO_RE.sub(r"\1 tên [đã ẩn tên]", s)
    return s


def sanitize_url(url: str, fallback_cat_url: str) -> tuple[str, bool]:
    if LONG_NUM_RE.search(url) or PHONE_RE.search(url):
        return fallback_cat_url, True
    return url, False


def is_cbc_heme(title: str, question: str, require_pregnancy_or_lab: bool = False) -> bool:
    combined = f"{title}\n{question}"
    q_lower = question.lower()
    if STRONG_HEME_RE.search(combined):
        return True
    if "bạch cầu" in q_lower and "nước tiểu" not in q_lower:
        return True
    if "xét nghiệm máu" in q_lower and not EXCLUDE_ONLY_RE.search(q_lower):
        return True
    if not require_pregnancy_or_lab and ("phân tích máu" in combined.lower() or "chỉ số máu" in combined.lower()):
        return True
    return False


# ---------------- TỪ DŨ ----------------
def parse_tudu_category_page(page: int):
    url = f"{TUDU_BASE}{TUDU_CAT}" if page == 1 else f"{TUDU_BASE}{TUDU_CAT}{page}/"
    try:
        raw = fetch(url)
    except Exception:
        return []
    posts = []
    matches = list(re.finditer(r'<a[^>]+href=["\'](/vn/suc-khoe-mang-thai/([^/"\']+)/)["\'][^>]*>(.*?)</a>', raw, re.S | re.I))
    seen_in_page = set()
    for i, m in enumerate(matches):
        path, slug, anchor_html = m.group(1), m.group(2), m.group(3)
        if slug.isdigit() or path in seen_in_page:
            continue
        seen_in_page.add(path)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else min(len(raw), start + 2500)
        snippet = clean_html_text(anchor_html + " " + raw[m.end():end])
        posts.append((page, TUDU_BASE + path, slug, snippet))
    return posts


def extract_tudu_question(raw_html: str):
    title_m = re.search(r"<h1[^>]*>(.*?)</h1>", raw_html, flags=re.S | re.I)
    title = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", title_m.group(1)))).strip() if title_m else ""
    body = raw_html[title_m.end():] if title_m else raw_html
    for stop_marker in ("Các bài viết khác", "Swiper_Option_Adv"):
        idx = body.find(stop_marker)
        if idx != -1:
            body = body[:idx]
    text = clean_html_text(body)
    ans_m = re.search(r"(?:^|\n)\s*Trả lời\b", text, flags=re.IGNORECASE)
    question = text[:ans_m.start()].strip() if ans_m else text[:1200].strip()
    q_lines = [
        ln for ln in question.splitlines()
        if not re.fullmatch(r"\d{1,2}\s+tháng\s+\d{1,2}(?:,\s*\d{4})?|\d{1,2}/\d{1,2}/\d{4}|Lượt xem:.*", ln, re.I)
    ]
    return scrub_pii(title), scrub_pii(" ".join(q_lines).strip())


def inspect_tudu_candidate(item):
    page, url, slug, _ = item
    try:
        raw = fetch(url)
        title, question = extract_tudu_question(raw)
    except Exception as exc:
        return {"source": "tudu", "page": page, "url": url, "slug": slug, "error": str(exc)}
    safe_url, url_redacted = sanitize_url(url, TUDU_BASE + TUDU_CAT)
    return {
        "source": "tudu",
        "page": page,
        "url": safe_url,
        "url_redacted": url_redacted,
        "slug": slug,
        "title": title,
        "question": question,
        "is_heme": is_cbc_heme(title, question),
    }


def mine_tudu(pages: int):
    all_posts = []
    seen = set()
    with ThreadPoolExecutor(max_workers=6) as pool:
        for idx, page_items in enumerate(pool.map(parse_tudu_category_page, range(1, pages + 1)), start=1):
            for item in page_items:
                if item[1] not in seen:
                    seen.add(item[1])
                    all_posts.append(item)
            if idx % 50 == 0 or idx == pages:
                print(f"  [Từ Dũ danh mục] {idx}/{pages} trang → {len(all_posts)} bài", flush=True)
    candidates = [it for it in all_posts if PREFILTER_RE.search(it[3]) or PREFILTER_RE.search(it[2].replace("-", " "))]
    print(f"  [Từ Dũ chi tiết] Đang kiểm {len(candidates)} ứng viên...", flush=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(inspect_tudu_candidate, candidates))
    matched = [r for r in results if r.get("is_heme")]
    errors = [r for r in results if r.get("error")]
    return {
        "pages": pages,
        "total_scanned": len(all_posts),
        "candidates": len(candidates),
        "errors": len(errors),
        "matched": matched,
    }


# ---------------- MEDLATEC ----------------
def parse_medlatec_page(cat_path: str, page: int):
    url = f"{MED_BASE}{cat_path}?pagenumber={page}"
    try:
        raw = fetch(url)
    except Exception as exc:
        return [], str(exc)

    start_idx = raw.find('class="faq-items"')
    if start_idx == -1:
        return [], None
    sub = raw[start_idx:]
    for stop in ('class="pagination"', 'sidebar-faq', 'class="col-xs-12 col-md-3'):
        sidx = sub.find(stop)
        if sidx != -1:
            sub = sub[:sidx]

    starts = [m.start() for m in re.finditer(r'<div class="faq-item"\s+data-item-id="(\d+)">', sub)]
    items = []
    for i, st in enumerate(starts):
        en = starts[i + 1] if i + 1 < len(starts) else len(sub)
        block = sub[st:en]
        id_m = re.search(r'data-item-id="(\d+)"', block)
        item_id = id_m.group(1) if id_m else ""
        # BẮT BUỘC: Xóa thẻ chứa tên người hỏi trước khi parse văn bản
        block = re.sub(r'<div class="faq-item-author">.*?</div>', "", block, flags=re.S | re.I)

        spec_m = re.search(r'<div class="faq-item-specialty">(.*?)</div>', block, flags=re.S | re.I)
        date_m = re.search(r'<div class="faq-item-date">(.*?)</div>', block, flags=re.S | re.I)
        title_m = re.search(r'<div class="faq-item-title">(.*?)</div>', block, flags=re.S | re.I)
        desc_m = re.search(r'<div class="faq-item-desc">(.*?)</div>', block, flags=re.S | re.I)
        href_m = re.search(r'href=["\'](/hoi-dap/[^"\']+-q\d+)["\']', block, flags=re.I)

        specialty = clean_html_text(spec_m.group(1)) if spec_m else ""
        date_txt = clean_html_text(date_m.group(1)) if date_m else ""
        title = scrub_pii(clean_html_text(title_m.group(1))) if title_m else ""
        question = scrub_pii(clean_html_text(desc_m.group(1))) if desc_m else ""
        raw_link = (MED_BASE + href_m.group(1)) if href_m else (MED_BASE + cat_path)
        safe_url, url_redacted = sanitize_url(raw_link, MED_BASE + cat_path)

        items.append({
            "source": "medlatec",
            "category": cat_path,
            "page": page,
            "item_id": item_id,
            "specialty": specialty,
            "date": date_txt,
            "title": title,
            "question": question,
            "url": safe_url,
            "url_redacted": url_redacted,
            "is_heme": is_cbc_heme(title, question),
            "mentions_pregnancy": bool(PREGNANCY_RE.search(f"{title}\n{question}")),
        })
    return items, None


def mine_medlatec_category(cat_path: str, pages: int):
    all_items = []
    seen_ids = set()
    errors = 0
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda p: parse_medlatec_page(cat_path, p), range(1, pages + 1)))
    for page_items, err in results:
        if err:
            errors += 1
        for it in page_items:
            uid = it["item_id"] or f"{it['page']}:{it['title']}"
            if uid not in seen_ids:
                seen_ids.add(uid)
                all_items.append(it)
    return {
        "category": cat_path,
        "pages": pages,
        "total_scanned": len(all_items),
        "errors": errors,
        "items": all_items,
        "matched": [it for it in all_items if it["is_heme"]],
    }


# ---------------- VERIFY ----------------
def verify_table():
    ev_dir = Path(__file__).resolve().parent
    table_path = ev_dir / "public-qa-cbc-table.md"
    text = table_path.read_text(encoding="utf-8")
    row_re = re.compile(r"^\|\s*`((?:TD|ML)\d+)`\s*\|")
    rows = [ln for ln in text.splitlines() if row_re.match(ln)]

    counts = {}
    by_source = {}
    for ln in rows:
        parts = [c.strip() for c in ln.strip("|").split("|")]
        code = parts[0].strip("`")
        src = "tudu" if code.startswith("TD") else "medlatec"
        label = parts[5].strip("`")
        counts[label] = counts.get(label, 0) + 1
        by_source.setdefault(src, {})[label] = by_source.setdefault(src, {}).get(label, 0) + 1

    total = len(rows)
    print(f"Kiểm bảng {table_path.name}: tổng N = {total} dòng")
    for k in sorted(counts):
        print(f"  [Gộp] {k}: {counts[k]}/{total} ({counts[k] * 100 / total:.2f}%)")
    for src, s_counts in by_source.items():
        s_tot = sum(s_counts.values())
        print(f"  Nguồn {src}: {s_tot} dòng")
        for k in sorted(s_counts):
            print(f"    {k}: {s_counts[k]}/{s_tot} ({s_counts[k] * 100 / s_tot:.2f}%)")

    # Kiểm tra Không-PII trên toàn bộ file evidence markdown
    pii_issues = []
    for md_name in ("public-qa-cbc-table.md", "data-mining.md", "summary.md"):
        p = ev_dir / md_name
        if not p.exists():
            continue
        for lineno, line in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
            if PHONE_RE.search(line):
                pii_issues.append(f"{md_name}:{lineno} có chuỗi nghi SĐT")
            for m in LONG_NUM_RE.finditer(line):
                val = m.group(0)
                if "doi.org" not in line and "1548096" not in val:
                    pii_issues.append(f"{md_name}:{lineno} có dãy số dài >=7 ký tự ({val})")
            if EMAIL_RE.search(line):
                pii_issues.append(f"{md_name}:{lineno} có email")
    if pii_issues:
        print("CẢNH BÁO PII:")
        for iss in pii_issues:
            print(" ", iss)
        sys.exit(1)
    print("Kiểm tra Không-PII (public-qa-cbc-table.md, data-mining.md, summary.md): 0 vi phạm.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["tudu", "medlatec", "all"], default="all")
    parser.add_argument("--tudu-pages", type=int, default=300)
    parser.add_argument("--med-spk-pages", type=int, default=53)
    parser.add_argument("--med-hh-pages", type=int, default=6)
    parser.add_argument("--out", type=str, default="")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    if args.verify:
        verify_table()
        return

    payload = {}
    if args.source in ("tudu", "all"):
        td = mine_tudu(args.tudu_pages)
        payload["tudu"] = td
        print(f"[Từ Dũ] {td['pages']} trang → M={td['total_scanned']} bài | ứng viên={td['candidates']} | lỗi={td['errors']} | khớp={len(td['matched'])}", flush=True)

    if args.source in ("medlatec", "all"):
        spk = mine_medlatec_category(MED_SPK_CAT, args.med_spk_pages)
        hh = mine_medlatec_category(MED_HH_CAT, args.med_hh_pages)
        payload["medlatec_spk"] = {k: v for k, v in spk.items() if k != "items"}
        payload["medlatec_hh"] = {k: v for k, v in hh.items() if k != "items"}
        payload["medlatec_hh_all"] = hh["items"]
        print(f"[MEDLATEC Sản phụ khoa] {spk['pages']} trang → M={spk['total_scanned']} bài | lỗi={spk['errors']} | khớp CBC={len(spk['matched'])}", flush=True)
        print(f"[MEDLATEC Huyết học] {hh['pages']} trang → M={hh['total_scanned']} bài | lỗi={hh['errors']} | khớp CBC={len(hh['matched'])}", flush=True)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Đã xuất JSON sạch PII tới: {out_path}", flush=True)


if __name__ == "__main__":
    main()
