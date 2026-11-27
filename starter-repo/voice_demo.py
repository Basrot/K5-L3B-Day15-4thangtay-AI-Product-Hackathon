"""Nhập phiếu, kiểm tra dữ liệu và nhận kết quả với hỏi đáp giọng nói."""

import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

import streamlit as st

from codebase.agent import analyze_report
from codebase.catalog import ANALYTES, DEFAULT_UNITS, GROUPS
from codebase.references import SUPPORTED_ANALYTES
from codebase.service import CBCService
from codebase.speech import transcribe_wav
from codebase.tts import synthesize_wav
from codebase.vision import extract_report
from codebase import ai

ROOT = Path(__file__).parent
LABELS = {"below": "Thấp hơn khoảng", "within": "Trong khoảng", "above": "Cao hơn khoảng"}


def display_reply(result):
    st.write(result["output"])
    if result.get("reference_note"):
        st.info(result["reference_note"])
    for source in result.get("sources", []):
        st.link_button(source["title"], source["url"])
    reference_source = result.get("reference_source")
    if reference_source and reference_source not in result.get("sources", []):
        if reference_source.get("url"):
            st.link_button(reference_source["title"], reference_source["url"])
        else:
            st.caption(reference_source["title"])


def reference_mode_for(report):
    if report.get("reference_mode") in ("study", "lab"):
        return report["reference_mode"]
    has_bounds = any(row.get(field) not in (None, "") for row in report.get("rows", [])
                     for field in ("ref_low", "ref_high", "ref_unit"))
    return "lab" if has_bounds else "study"


def report_signature(report):
    reference_mode = reference_mode_for(report)
    fields = ("value", "unit") if reference_mode == "study" else ("value", "unit", "ref_low", "ref_high", "ref_unit")
    cleaned = {key: report.get(key) for key in ("adult_confirmed", "pregnancy_status", "gestational_age")}
    cleaned["reference_mode"] = reference_mode
    cleaned["rows"] = [{"analyte": row["analyte"], **{field: "" if row.get(field) is None else str(row[field])
                                                       for field in fields}} for row in sorted(report["rows"], key=lambda row: row["analyte"])]
    return json.dumps(cleaned, ensure_ascii=False, sort_keys=True)


def clear_answers():
    for key in ("analysis", "reply", "reply_audio", "analysis_audio"):
        st.session_state.pop(key, None)


def set_draft(report, source=None, reference_mode=None):
    st.session_state["draft"] = {**report, "reference_mode": reference_mode or reference_mode_for(report)}
    st.session_state["draft_version"] = st.session_state.get("draft_version", 0) + 1
    st.session_state["draft_source"] = source
    st.session_state["question"] = ""
    st.session_state.pop("draft_notice", None)
    clear_answers()


st.set_page_config(page_title="Đọc phiếu xét nghiệm thai kỳ", page_icon="🩸", layout="wide")
st.title("Đọc phiếu xét nghiệm thai kỳ")
st.caption("Đọc 8 chỉ số CBC được nhóm chọn; so sánh với nghiên cứu theo tam cá nguyệt hoặc khoảng trên phiếu.")
service = CBCService()
if "cbc_session" not in st.session_state:
    st.session_state["cbc_session"] = service.create_session()
    st.session_state["displayed_revision"] = 0
    set_draft(json.loads((ROOT / "data/full-panel-demo.json").read_text(encoding="utf-8")), reference_mode="study")
session_id = st.session_state["cbc_session"]

left, right = st.columns(2)
if left.button("Dùng phiếu giả lập 8 chỉ số"):
    sample = json.loads((ROOT / "data/full-panel-demo.json").read_text(encoding="utf-8"))
    sample["rows"] = [row for row in sample["rows"] if row["analyte"] in SUPPORTED_ANALYTES]
    set_draft(sample, reference_mode="study")
if right.button("Nhập phiếu mới"):
    st.session_state["cbc_session"] = service.create_session()
    st.session_state["displayed_revision"] = 0
    session_id = st.session_state["cbc_session"]
    set_draft({"rows": [], "gestational_age": "", "adult_confirmed": False, "reference_mode": "study"})

with st.expander("Phiên đã lưu"):
    st.caption("Giữ mã phiên để mở lại phiếu và lịch sử sau khi tải lại trang.")
    st.code(session_id)
    restore_id = st.text_input("Mã phiên muốn mở", max_chars=32)
    if st.button("Mở phiên"):
        try:
            restored = service.get_session(restore_id.strip())
            if restored["report"] is None:
                st.info("Phiên này chưa có phiếu đã xác nhận.")
            else:
                st.session_state["cbc_session"] = restore_id.strip()
                session_id = restore_id.strip()
                set_draft(restored["report"])
                st.session_state["displayed_revision"] = restored["revision"]
                st.session_state["input_mode"] = "Nhập tay"
                st.session_state["current_signature"] = report_signature(restored["report"])
                restored_analysis = analyze_report(restored["report"])
                if restored_analysis["status"] == "analyzed":
                    st.session_state["analysis"] = restored_analysis
                else:
                    st.session_state["draft_notice"] = restored_analysis["output"]
                st.rerun()
        except KeyError:
            st.error("Không tìm thấy phiên. Kiểm tra lại mã.")

reference_mode = st.radio(
    "Nguồn khoảng tham chiếu", ["study", "lab"],
    index=0 if reference_mode_for(st.session_state["draft"]) == "study" else 1,
    format_func=lambda value: "Nghiên cứu theo tam cá nguyệt" if value == "study" else "Khoảng ghi trên phiếu",
    key=f"reference-mode-{st.session_state['draft_version']}", horizontal=True,
)
if reference_mode == "study":
    st.caption("Nhập kết quả và đơn vị; khoảng nghiên cứu được chọn từ tuổi thai sau khi xác nhận. "
               "Khoảng này không phải ngưỡng chẩn đoán hoặc khoảng đã được xác nhận cho phòng xét nghiệm của bạn.")
mode = st.radio("Cách nhập phiếu", ["Nhập tay", "Tải ảnh"], key="input_mode", horizontal=True)
upload_ready = True
if mode == "Tải ảnh":
    if ai.MODEL_PROVIDER == "openai_compatible":
        destination = os.environ.get("VISION_API_BASE", "").strip() or os.environ.get("LLM_API_BASE", "")
        st.caption(f"Ảnh sẽ được gửi tới {urlsplit(destination).hostname or 'dịch vụ AI đã cấu hình'} "
                   "khi bấm Đọc ảnh vào các ô bên dưới.")
    image = st.file_uploader("Ảnh phiếu xét nghiệm", type=["png", "jpg", "jpeg"])
    digest = hashlib.sha256(image.getvalue()).hexdigest() if image else None
    upload_ready = digest is not None and digest == st.session_state.get("draft_source")
    if st.button("Đọc ảnh vào các ô bên dưới", disabled=image is None):
        try:
            with st.spinner("Đang đọc số, đơn vị và khoảng tham chiếu…"):
                extracted = extract_report(image.getvalue(), image.type)
            set_draft({"rows": extracted["rows"], "notice": "", "adult_confirmed": False,
                       "gestational_age": "", "pregnancy_status": "unknown", "reference_mode": reference_mode}, source=digest)
            for warning in extracted["warnings"]:
                st.warning(warning)
            upload_ready = True
        except (ValueError, RuntimeError, OSError) as exc:
            st.error(str(exc))

draft = st.session_state["draft"]
version = st.session_state["draft_version"]
if draft.get("notice"):
    st.info(draft["notice"])
if st.session_state.get("draft_notice"):
    st.warning(st.session_state["draft_notice"])
context = st.columns(3)
adult = context[0].checkbox("Người làm xét nghiệm từ 18 tuổi", value=draft.get("adult_confirmed", False),
                            key=f"adult-{version}")
pregnancy = context[1].selectbox("Tình trạng thai kỳ", ["Đang mang thai", "Chưa xác định", "Không mang thai"],
                                index=0 if draft.get("pregnancy_status") == "pregnant" else 1,
                                key=f"pregnancy-{version}")
age = context[2].text_input("Tuổi thai lúc xét nghiệm, ví dụ 21w3d",
                           value=draft.get("gestational_age", ""), key=f"age-{version}")
by_code = {row["analyte"]: row for row in draft["rows"]}
selected = st.multiselect("Các chỉ số có trên phiếu", list(SUPPORTED_ANALYTES), default=list(by_code),
                          format_func=lambda code: f"{code} · {ANALYTES[code]}", key=f"codes-{version}")
rows = []
for group in dict.fromkeys(GROUPS.values()):
    group_codes = [code for code in selected if GROUPS[code] == group]
    if not group_codes:
        continue
    with st.expander(f"{group} · {len(group_codes)} chỉ số", expanded=len(selected) <= 5):
        for code in group_codes:
            initial = by_code.get(code, {})
            st.markdown(f"**{code} — {ANALYTES[code]}**")
            fields = ("value", "unit") if reference_mode == "study" else ("value", "unit", "ref_low", "ref_high", "ref_unit")
            labels = ("Kết quả", "Đơn vị kết quả") if reference_mode == "study" else ("Kết quả", "Đơn vị kết quả", "Giới hạn dưới", "Giới hạn trên", "Đơn vị khoảng")
            defaults = ("", DEFAULT_UNITS[code]) if reference_mode == "study" else ("", DEFAULT_UNITS[code], "", "", DEFAULT_UNITS[code])
            columns = st.columns(len(fields))
            values = {}
            for column, field, label, default in zip(columns, fields, labels, defaults):
                raw = initial.get(field)
                if st.session_state.get("draft_source"):
                    default = ""
                values[field] = column.text_input(label, value=str(default if raw is None else raw),
                                                   key=f"{version}-{code}-{field}")
            rows.append({"analyte": code, **values})

report = {
    "adult_confirmed": adult,
    "pregnancy_status": {"Đang mang thai": "pregnant", "Chưa xác định": "unknown",
                         "Không mang thai": "not_pregnant"}[pregnancy],
    "gestational_age": age, "reference_mode": reference_mode, "rows": rows,
}
signature = report_signature(report)
try:
    current = service.get_session(session_id)
except KeyError:
    clear_answers()
    st.error("Phiên đã bị xóa. Mở một phiên đã lưu hoặc chọn Nhập phiếu mới.")
    st.stop()
if "displayed_revision" not in st.session_state:
    # Upgrade an already-open UI once; subsequent writes retain this snapshot.
    st.session_state["displayed_revision"] = current["revision"]
displayed_revision = st.session_state["displayed_revision"]
revision_conflict = current["revision"] != displayed_revision
if not revision_conflict and (signature != st.session_state.get("current_signature") or not upload_ready):
    if current["report"] is not None:
        try:
            invalidated = service.invalidate_report(session_id, expected_revision=displayed_revision)
            displayed_revision = invalidated["revision"]
            st.session_state["displayed_revision"] = displayed_revision
        except ValueError:
            revision_conflict = True
    clear_answers()
    if not revision_conflict:
        st.session_state["current_signature"] = signature
if revision_conflict:
    clear_answers()
    st.warning("Phiếu đã được thay đổi ở nơi khác. Dùng Mở phiên với mã hiện tại để tải bản mới nhất; "
               "bản đang sửa chưa được ghi đè lên dữ liệu đã lưu.")

st.caption("Kiểm tra từng số, đơn vị và tuổi thai trước khi xác nhận." if reference_mode == "study" else
           "Kiểm tra từng số, đơn vị và khoảng tham chiếu trên phiếu trước khi xác nhận.")
if st.button("Xác nhận và nhận kết quả", disabled=not upload_ready or revision_conflict, type="primary"):
    result = analyze_report(report)
    if result["status"] == "analyzed":
        try:
            confirmed = service.confirm_report(session_id, report, confirmed=True, expected_revision=displayed_revision)
            snapshot = confirmed["session"]
            st.session_state["displayed_revision"] = snapshot["revision"]
            displayed_revision = snapshot["revision"]
            st.session_state["analysis"] = analyze_report(snapshot["report"])
            st.session_state.pop("draft_notice", None)
        except (KeyError, ValueError) as exc:
            clear_answers()
            revision_conflict = True
            st.error(str(exc) + " Mở lại phiên để tải dữ liệu mới nhất trước khi xác nhận.")
    else:
        st.error(result["output"])

if "analysis" in st.session_state:
    analysis = st.session_state["analysis"]
    st.subheader("Kết quả đối chiếu")
    display_reply(analysis)
    range_label = (f"Khoảng nghiên cứu · tam cá nguyệt {analysis.get('trimester', '')}"
                   if analysis.get("reference_mode") == "study" else "Khoảng trên phiếu")
    table = f"| Chỉ số | Kết quả đối chiếu | {range_label} | Trạng thái |\n|---|---|---|---|\n"
    for row in analysis["rows"]:
        table += (f"| {row['analyte']} · {ANALYTES[row['analyte']]} | {row['value']} {row['unit']} | "
                  f"{row['ref_low']}–{row['ref_high']} {row['unit']} | {LABELS[row['status']]} |\n")
    st.markdown(table)
    provenance = analysis.get("reference_source") or {}
    download = analysis["output"] + "\n\n" + table + "\n" + analysis.get("reference_note", "")
    if provenance:
        download += "\n" + provenance["title"]
        if provenance.get("url"):
            download += "\n" + provenance["url"]
    st.download_button("Tải kết quả dạng văn bản", download,
                       file_name="ket-qua-doi-chieu.txt", mime="text/plain")
    if st.button("Nghe tóm tắt kết quả"):
        try:
            with st.spinner("Đang tạo giọng đọc…"):
                st.session_state["analysis_audio"] = synthesize_wav(analysis["output"])
        except Exception as exc:
            st.warning(f"Chưa tạo được giọng đọc: {exc}")
    if "analysis_audio" in st.session_state:
        st.audio(st.session_state["analysis_audio"], format="audio/wav")

st.subheader("Hỏi thêm về phiếu")
audio = st.audio_input("Ghi câu hỏi tiếng Việt", sample_rate=16000, key=f"audio-{version}")
if st.button("Chuyển thành chữ", disabled=audio is None):
    try:
        with st.spinner("Đang nhận dạng…"):
            st.session_state["question"] = transcribe_wav(audio.getvalue())
        if not st.session_state["question"]:
            st.info("Chưa nhận được lời nói. Bạn có thể ghi lại hoặc gõ câu hỏi.")
    except (ValueError, RuntimeError, OSError) as exc:
        st.error(str(exc))
question = st.text_area("Kiểm tra hoặc sửa câu hỏi trước khi gửi", key="question",
                        placeholder="Ví dụ: MCV trên phiếu có ý nghĩa gì?")
read_aloud = st.checkbox("Đọc câu trả lời bằng giọng nói", value=True)
submitted = st.button("Hỏi AI", disabled="analysis" not in st.session_state or not question.strip())
if submitted:
    st.session_state.pop("reply_audio", None)
    st.session_state.pop("reply", None)
    try:
        with st.spinner("Đang giải thích phiếu…"):
            result = service.ask(session_id, question, expected_revision=displayed_revision)
        st.session_state["reply"] = result
        display_reply(result)
        if read_aloud:
            try:
                with st.spinner("Đang tạo giọng đọc…"):
                    st.session_state["reply_audio"] = synthesize_wav(result["output"])
            except Exception as exc:
                st.warning(f"Chưa tạo được giọng đọc: {exc}")
    except (KeyError, ValueError, RuntimeError, OSError) as exc:
        st.error(str(exc))
if "reply" in st.session_state:
    if not submitted:
        display_reply(st.session_state["reply"])
    if read_aloud and "reply_audio" in st.session_state:
        st.audio(st.session_state["reply_audio"], format="audio/wav", autoplay=True)

if "analysis" in st.session_state:
    with st.expander("Lịch sử hỏi đáp của phiếu"):
        messages = service.history(session_id)
        if not messages:
            st.caption("Chưa có câu hỏi được lưu.")
        for message in messages:
            st.markdown("**Bạn hỏi**")
            st.write(message["question"])
            st.markdown("**Trả lời**")
            st.write(message["result"]["output"])
