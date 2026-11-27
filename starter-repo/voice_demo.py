"""Nhập phiếu, kiểm tra dữ liệu và nhận kết quả với hỏi đáp giọng nói."""

import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

import streamlit as st

from codebase.agent import analyze_report
from codebase.catalog import ANALYTES, DEFAULT_UNITS, GROUPS
from codebase.service import CBCService
from codebase.speech import transcribe_wav
from codebase.tts import synthesize_wav
from codebase.vision import extract_report
from codebase import ai

ROOT = Path(__file__).parent
LABELS = {"below": "Thấp hơn khoảng", "within": "Trong khoảng", "above": "Cao hơn khoảng"}


def display_reply(result):
    st.write(result["output"])
    for source in result.get("sources", []):
        st.link_button(source["title"], source["url"])


def clear_answers():
    for key in ("analysis", "reply", "reply_audio", "analysis_audio"):
        st.session_state.pop(key, None)


def set_draft(report, source=None):
    st.session_state["draft"] = report
    st.session_state["draft_version"] = st.session_state.get("draft_version", 0) + 1
    st.session_state["draft_source"] = source
    st.session_state["question"] = ""
    clear_answers()


st.set_page_config(page_title="Đọc phiếu xét nghiệm thai kỳ", page_icon="🩸", layout="wide")
st.title("Đọc phiếu xét nghiệm thai kỳ")
st.caption("Đối chiếu 21 chỉ số công thức máu và 3 chỉ số đông máu với khoảng ghi trên phiếu.")
service = CBCService()
if "cbc_session" not in st.session_state:
    st.session_state["cbc_session"] = service.create_session()
    set_draft(json.loads((ROOT / "data/full-panel-demo.json").read_text(encoding="utf-8")))
session_id = st.session_state["cbc_session"]

left, right = st.columns(2)
if left.button("Dùng phiếu giả lập 24 chỉ số"):
    set_draft(json.loads((ROOT / "data/full-panel-demo.json").read_text(encoding="utf-8")))
if right.button("Nhập phiếu mới"):
    st.session_state["cbc_session"] = service.create_session()
    session_id = st.session_state["cbc_session"]
    set_draft({"rows": [], "gestational_age": "", "adult_confirmed": False})

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
                st.session_state["current_signature"] = json.dumps(
                    restored["report"], ensure_ascii=False, sort_keys=True
                )
                st.session_state["analysis"] = analyze_report(restored["report"])
                st.rerun()
        except KeyError:
            st.error("Không tìm thấy phiên. Kiểm tra lại mã.")

mode = st.radio("Cách nhập phiếu", ["Nhập tay", "Tải ảnh"], horizontal=True)
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
                       "gestational_age": "", "pregnancy_status": "unknown"}, source=digest)
            for warning in extracted["warnings"]:
                st.warning(warning)
            upload_ready = True
        except (ValueError, RuntimeError, OSError) as exc:
            st.error(str(exc))

draft = st.session_state["draft"]
version = st.session_state["draft_version"]
if draft.get("notice"):
    st.info(draft["notice"])
context = st.columns(3)
adult = context[0].checkbox("Người làm xét nghiệm từ 18 tuổi", value=draft.get("adult_confirmed", False),
                            key=f"adult-{version}")
pregnancy = context[1].selectbox("Tình trạng thai kỳ", ["Đang mang thai", "Chưa xác định", "Không mang thai"],
                                index=0 if draft.get("pregnancy_status") == "pregnant" else 1,
                                key=f"pregnancy-{version}")
age = context[2].text_input("Tuổi thai lúc xét nghiệm, ví dụ 21w3d",
                           value=draft.get("gestational_age", ""), key=f"age-{version}")
by_code = {row["analyte"]: row for row in draft["rows"]}
selected = st.multiselect("Các chỉ số có trên phiếu", list(ANALYTES), default=list(by_code),
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
            columns = st.columns(5)
            values = {}
            for column, field, label, default in zip(
                columns, ("value", "unit", "ref_low", "ref_high", "ref_unit"),
                ("Kết quả", "Đơn vị kết quả", "Giới hạn dưới", "Giới hạn trên", "Đơn vị khoảng"),
                ("", DEFAULT_UNITS[code], "", "", DEFAULT_UNITS[code]),
            ):
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
    "gestational_age": age, "rows": rows,
}
signature = json.dumps(report, ensure_ascii=False, sort_keys=True)
current = service.get_session(session_id)
if signature != st.session_state.get("current_signature") or not upload_ready:
    if current["report"] is not None:
        service.invalidate_report(session_id, expected_revision=current["revision"])
    clear_answers()
    st.session_state["current_signature"] = signature

st.caption("Kiểm tra từng số, đơn vị và khoảng tham chiếu trên phiếu trước khi xác nhận.")
if st.button("Xác nhận và nhận kết quả", disabled=not upload_ready, type="primary"):
    result = analyze_report(report)
    if result["status"] == "analyzed":
        current = service.get_session(session_id)
        service.confirm_report(session_id, report, confirmed=True, expected_revision=current["revision"])
        st.session_state["analysis"] = result
    else:
        st.error(result["output"])

if "analysis" in st.session_state:
    analysis = st.session_state["analysis"]
    st.subheader("Kết quả đối chiếu")
    display_reply(analysis)
    table = "| Chỉ số | Kết quả đối chiếu | Khoảng trên phiếu | Trạng thái |\n|---|---|---|---|\n"
    for row in analysis["rows"]:
        table += (f"| {row['analyte']} · {ANALYTES[row['analyte']]} | {row['value']} {row['unit']} | "
                  f"{row['ref_low']}–{row['ref_high']} {row['unit']} | {LABELS[row['status']]} |\n")
    st.markdown(table)
    st.download_button("Tải kết quả dạng văn bản", analysis["output"] + "\n\n" + table,
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
            revision = service.get_session(session_id)["revision"]
            result = service.ask(session_id, question, expected_revision=revision)
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
