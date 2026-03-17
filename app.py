import streamlit as st
import json

st.set_page_config(page_title="Trac nghiem", page_icon="📝")

# --------- STATE ---------
if "started" not in st.session_state:
    st.session_state.started = False

# --------- MAN HINH CHAO ---------
if not st.session_state.started:

    st.title("📝 Chào mừng đến bài trắc nghiệm")

    name = st.text_input("Họ tên:")
    lop = st.text_input("Lớp:")

    if st.button("Bắt đầu làm bài"):

        if name.strip() == "":
            st.warning("Vui lòng nhập họ tên")
        else:
            st.session_state.started = True
            st.session_state.name = name
            st.session_state.lop = lop
            st.rerun()

# --------- MAN HINH LAM BAI ---------
else:

    st.title("📝 Công cụ trắc nghiệm")

    st.write(f"Người làm bài: **{st.session_state.name}**")

    with open("questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    user_answers = []

    for i, q in enumerate(questions, start=1):

        st.subheader(f"Câu {i}: {q['question']}")

        options = ["-- Chọn đáp án --"] + q["options"]

        answer = st.radio(
            "Chọn:",
            options,
            key=f"q{i}"
        )

        user_answers.append(answer)

    if st.button("Nộp bài"):

        score = 0
        st.markdown("---")

        for i, q in enumerate(questions):

            if user_answers[i] == q["answer"]:
                score += 1
                st.success(f"Câu {i+1}: Đúng")
            else:
                st.error(f"Câu {i+1}: Sai (Đáp án: {q['answer']})")

        st.markdown("---")
        st.write(f"### Kết quả: {score}/{len(questions)}")
