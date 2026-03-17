import streamlit as st
import json

st.set_page_config(page_title="Trac nghiem", page_icon="📝", layout="centered")

st.title("📝 Công cụ trắc nghiệm")
st.write("Chọn đáp án cho từng câu hỏi, sau đó bấm **Nộp bài**.")

# Đọc file câu hỏi
with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

user_answers = []

# Hiển thị câu hỏi
for i, q in enumerate(questions, start=1):
    st.subheader(f"Câu {i}: {q['question']}")
    answer = st.radio(
        "Chọn đáp án:",
        q["options"],
        key=f"question_{i}"
    )
    user_answers.append(answer)

# Nút nộp bài
if st.button("Nộp bài"):
    score = 0
    st.markdown("---")
    st.subheader("Kết quả")

    for i, q in enumerate(questions):
        correct_answer = q["answer"]
        user_answer = user_answers[i]

        if user_answer == correct_answer:
            score += 1
            st.success(f"Câu {i+1}: Đúng")
        else:
            st.error(f"Câu {i+1}: Sai — Đáp án đúng là: {correct_answer}")

    st.markdown("---")
    st.write(f"### Bạn làm đúng {score}/{len(questions)} câu")
