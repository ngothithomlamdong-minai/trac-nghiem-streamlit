import math
import json
from datetime import datetime, timedelta

import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Cong cu trac nghiem", page_icon="📝", layout="centered")

QUESTIONS_PER_PAGE = 5
TEST_DURATION_MINUTES = 10


def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)


questions = load_questions()
total_questions = len(questions)
total_pages = math.ceil(total_questions / QUESTIONS_PER_PAGE)


def init_state():
    if "started" not in st.session_state:
        st.session_state.started = False

    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    if "name" not in st.session_state:
        st.session_state.name = ""

    if "lop" not in st.session_state:
        st.session_state.lop = ""

    if "start_time" not in st.session_state:
        st.session_state.start_time = None

    if "end_time" not in st.session_state:
        st.session_state.end_time = None

    if "score" not in st.session_state:
        st.session_state.score = 0

    if "auto_submitted" not in st.session_state:
        st.session_state.auto_submitted = False

    for i in range(total_questions):
        key = f"q_{i}"
        if key not in st.session_state:
            st.session_state[key] = None


def get_unanswered_questions():
    unanswered = []
    for i in range(total_questions):
        if st.session_state.get(f"q_{i}") is None:
            unanswered.append(i + 1)
    return unanswered


def calculate_score():
    score = 0
    for i, q in enumerate(questions):
        if st.session_state.get(f"q_{i}") == q["answer"]:
            score += 1
    return score


def submit_exam(auto=False):
    st.session_state.score = calculate_score()
    st.session_state.submitted = True
    st.session_state.auto_submitted = auto
    st.rerun()


def format_seconds(seconds):
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


init_state()

# =========================
# MAN HINH CHAO
# =========================
if not st.session_state.started:
    st.title("📝 Chào mừng đến bài trắc nghiệm")
    st.write("Vui lòng nhập thông tin trước khi bắt đầu làm bài.")
    st.info(f"Thời gian làm bài: {TEST_DURATION_MINUTES} phút | Tổng số câu: {total_questions}")

    name = st.text_input("Họ tên", value=st.session_state.name)
    lop = st.text_input("Lớp", value=st.session_state.lop)

    if st.button("Bắt đầu làm bài"):
        if name.strip() == "":
            st.warning("Vui lòng nhập họ tên.")
        else:
            st.session_state.name = name.strip()
            st.session_state.lop = lop.strip()
            st.session_state.started = True
            st.session_state.submitted = False
            st.session_state.current_page = 1
            st.session_state.start_time = datetime.now()
            st.session_state.end_time = st.session_state.start_time + timedelta(minutes=TEST_DURATION_MINUTES)
            st.session_state.score = 0
            st.session_state.auto_submitted = False

            for i in range(total_questions):
                st.session_state[f"q_{i}"] = None

            st.rerun()

# =========================
# MAN HINH KET QUA
# =========================
elif st.session_state.submitted:
    st.title("✅ Kết quả bài làm")
    st.write(f"**Họ tên:** {st.session_state.name}")
    if st.session_state.lop:
        st.write(f"**Lớp:** {st.session_state.lop}")

    if st.session_state.auto_submitted:
        st.warning("Hết giờ, hệ thống đã tự nộp bài.")
    else:
        st.success("Bạn đã nộp bài thành công.")

    st.markdown("---")
    st.subheader(f"Điểm số: {st.session_state.score}/{total_questions}")

    st.markdown("---")
    st.subheader("Chi tiết đáp án")

    for i, q in enumerate(questions, start=1):
        user_answer = st.session_state.get(f"q_{i-1}")
        correct_answer = q["answer"]

        st.markdown(f"**Câu {i}: {q['question']}**")
        st.write(f"- Đáp án của bạn: {user_answer if user_answer is not None else 'Chưa trả lời'}")
        st.write(f"- Đáp án đúng: {correct_answer}")

        if user_answer == correct_answer:
            st.success("Đúng")
        else:
            st.error("Sai")

        st.markdown("---")

# =========================
# MAN HINH LAM BAI
# =========================
else:
    st_autorefresh(interval=1000, key="countdown_refresh")

    now = datetime.now()
    remaining_seconds = int((st.session_state.end_time - now).total_seconds())

    if remaining_seconds <= 0:
        submit_exam(auto=True)

    st.title("📝 Công cụ trắc nghiệm")
    st.write(f"**Họ tên:** {st.session_state.name}")
    if st.session_state.lop:
        st.write(f"**Lớp:** {st.session_state.lop}")

    st.error(f"⏳ Thời gian còn lại: {format_seconds(remaining_seconds)}")

    unanswered = get_unanswered_questions()
    if unanswered:
        st.warning(f"Bạn còn {len(unanswered)} câu chưa trả lời: {', '.join(map(str, unanswered))}")
    else:
        st.success("Bạn đã trả lời đầy đủ tất cả các câu.")

    st.markdown("---")

    st.subheader("Chọn trang")
    page = st.radio(
        "Trang",
        options=list(range(1, total_pages + 1)),
        format_func=lambda x: f"Trang {x}",
        horizontal=True,
        key="current_page"
    )

    start_idx = (page - 1) * QUESTIONS_PER_PAGE
    end_idx = min(start_idx + QUESTIONS_PER_PAGE, total_questions)

    for i in range(start_idx, end_idx):
        q = questions[i]
        st.subheader(f"Câu {i + 1}: {q['question']}")
        st.radio(
            "Chọn đáp án:",
            options=q["options"],
            key=f"q_{i}",
            index=None
        )
        st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        if page > 1:
            if st.button("⬅ Trang trước"):
                st.session_state.current_page = page - 1
                st.rerun()

    with col2:
        st.write("")

    with col3:
        if page < total_pages:
            if st.button("Trang sau ➡"):
                st.session_state.current_page = page + 1
                st.rerun()

    st.markdown("---")

    submit_disabled = len(unanswered) > 0
    if st.button("Nộp bài", disabled=submit_disabled):
        submit_exam(auto=False)

    if submit_disabled:
        st.caption("Bạn phải trả lời hết tất cả các câu thì mới bấm Nộp bài được.")
