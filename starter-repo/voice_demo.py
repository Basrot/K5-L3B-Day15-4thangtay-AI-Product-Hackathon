"""Màn hình kiểm thử giọng nói trên phiếu CBC giả lập."""

import json
from pathlib import Path

import streamlit as st

from codebase.agent import answer
from codebase.speech import transcribe_wav

st.set_page_config(page_title="Hỏi về phiếu CBC", page_icon="🎙️")
st.title("Hỏi về phiếu CBC")
sample = json.loads((Path(__file__).parent / "data" / "cbc-demo-input.json").read_text(encoding="utf-8"))
st.caption("Thử giọng nói tiếng Việt với phiếu giả lập. Tuổi thai lúc xét nghiệm 21 tuần 3 ngày.")
st.markdown(
    "| Chỉ số | Kết quả | Khoảng ghi trên phiếu |\n"
    "|---|---|---|\n"
    + "\n".join(
        f"| {row['analyte']} | {row['value']} {row['unit']} | "
        f"{row['ref_low']}–{row['ref_high']} {row['ref_unit']} |"
        for row in sample["report"]["rows"]
    )
)
confirmed = st.checkbox("Tôi đã kiểm tra các số, đơn vị và khoảng tham chiếu trên phiếu mẫu.")

audio = st.audio_input("Ghi câu hỏi tiếng Việt", sample_rate=16000)
if st.button("Chuyển thành chữ", disabled=audio is None):
    try:
        with st.spinner("Đang nhận dạng…"):
            st.session_state["question"] = transcribe_wav(audio.getvalue())
        if not st.session_state["question"]:
            st.info("Chưa nhận được lời nói. Bạn có thể ghi lại hoặc gõ câu hỏi.")
    except (ValueError, RuntimeError, OSError) as exc:
        st.error(str(exc))

question = st.text_area("Kiểm tra hoặc sửa câu hỏi trước khi gửi", key="question",
                        placeholder="Ví dụ: Vì sao huyết sắc tố có dấu L?")
if st.button("Hỏi AI", disabled=not confirmed or not question.strip(), type="primary"):
    try:
        with st.spinner("Đang giải thích phiếu…"):
            result = answer(json.dumps({"report": sample["report"], "question": question}, ensure_ascii=False))
        st.write(result["output"])
        for source in result.get("sources", []):
            st.link_button(source["title"], source["url"])
    except (ValueError, RuntimeError, OSError) as exc:
        st.error(str(exc))
