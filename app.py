import json
import os
from datetime import datetime, timedelta

import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Cong cu trac nghiem", page_icon="📝", layout="centered")

TEST_DURATION_MINUTES = 10
QUESTIONS_FILE = "questions.json"
HISTORY_FILE = "history.json"


def load_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except:
        return []


def save_history(history_data):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)


def format_seconds(seconds):
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def init_state(total_questions):
    defaults = {
        "screen": "welcome",   # welcome, exam, result, history
        "name": "",
        "lop": "",
        "start_time_str": "",
        "end_time_str": "",
        "submitted": False,
        "auto_submitted": False,
        "score": 0
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    for i in range(total_questions):
        key = f"q_{i}"
        if key not in st.session_state:
            st.session_state[key] = None


def reset_exam(total_questions):
    st.session_state.screen = "welcome"
    st.session_state.name = ""
    st.session_state.lop = ""
    st.session_state.start_time_str = ""
    st.session_state.end_time_str = ""
    st.session_state.submitted = False
    st.session_state.auto_submitted = False
    st.session_state.score = 0

    for i in range(total_questions):
        st.session_state[f"q_{i}"] = None


def get_unanswered(total_questions):
    unanswered = []
    for i in range(total_questions):
        if st.session_state.get(f"q_{i}") is None:
            unanswered.append(i + 1)
    return unanswered


def calculate_score(questions):
    score = 0
    for i, q in enumerate(questions):
        if st.session_state.get(f"q_{i}") == q["answer"]:
            score += 1
    return score


def save_attempt(questions, score, auto_submitted):
    history = load_history()

    answers = []
    for i, q in enumerate(questions):
        answers.append({
            "question_no": i + 1,
            "question": q["question"],
            "user_answer": st.session_state.get(f"q_{i}"),
            "correct_answer": q["answer"],
            "is_correct": st.session_state.get(f"q_{i}") == q["answer"]
        })

    record = {
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": st.session_state.name,
        "lop": st.session_state.lop,
        "score": score,
        "total": len(questions),
        "auto_submitted": auto_submitted,
        "answers": answers
    }

    history.insert(0, record)
    save_history(history)


def submit_exam(questions, auto=False):
    unanswered = get_unanswered(len(questions))

    if (not auto) and unanswered:
        st.warning("Bạn phải trả lời hết tất cả các câu trước khi nộp.")
        return

    score = calculate_score(questions)
    st.session_state.score = score
    st.session_state.submitted = True
    st.session_state.auto_submitted = auto

    save_attempt(questions, score, auto)

    st.session_state.screen = "result"
    st.rerun()


questions = load_questions()
total_questions = len(questions)
init_state(total_questions)

# ===== THANH MENU TREN CUNG =====
col_a, col_b, col_c = st.columns(3)

with col_a:
    if st.button("Trang chào"):
        st.session_state.screen = "welcome"
        st.rerun()

with col_b:
    if st.button("Làm bài"):
        st.session_state.screen = "exam"
        st.rerun()

with col_c:
    if st.button("Lịch sử thi"):
        st.session_state.screen = "history"
        st.rerun()

st.markdown("---")

# ===== MAN HINH CHAO =====
if st.session_state.screen == "welcome":
    st.title("📝 Chào mừng đến bài trắc nghiệm")
    st.write("Vui lòng nhập thông tin trước khi bắt đầu.")
    st.info(f"Thời gian làm bài: {TEST_DURATION_MINUTES} phút | Tổng số câu: {total_questions}")

    name = st.text_input("Họ tên", value=st.session_state.name)
    lop = st.text_input("Lớp", value=st.session_state.lop)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Bắt đầu làm bài"):
            if name.strip() == "":
                st.warning("Vui lòng nhập họ tên.")
            else:
                st.session_state.name = name.strip()
                st.session_state.lop = lop.strip()
                st.session_state.submitted = False
                st.session_state.auto_submitted = False
                st.session_state.score = 0
                st.session_state.start_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.end_time_str = (
                    datetime.now() + timedelta(minutes=TEST_DURATION_MINUTES)
                ).strftime("%Y-%m-%d %H:%M:%S")

                for i in range(total_questions):
                    st.session_state[f"q_{i}"] = None

                st.session_state.screen = "exam"
                st.rerun()

    with col2:
        if st.button("Xem lịch sử thi"):
            st.session_state.screen = "history"
            st.rerun()

# ===== MAN HINH LAM BAI =====
elif st.session_state.screen == "exam":
    if st.session_state.name.strip() == "" or st.session_state.end_time_str == "":
        st.warning("Bạn chưa bắt đầu bài thi. Hãy quay lại Trang chào.")
    else:
        st_autorefresh(interval=1000, key="countdown_refresh")

        end_time = datetime.strptime(st.session_state.end_time_str, "%Y-%m-%d %H:%M:%S")
        remaining_seconds = int((end_time - datetime.now()).total_seconds())

        if remaining_seconds <= 0:
            submit_exam(questions, auto=True)

        st.title("📝 Công cụ trắc nghiệm")
        st.write(f"**Họ tên:** {st.session_state.name}")
        if st.session_state.lop:
            st.write(f"**Lớp:** {st.session_state.lop}")

        st.error(f"⏳ Thời gian còn lại: {format_seconds(max(0, remaining_seconds))}")

        unanswered = get_unanswered(total_questions)
        if unanswered:
            st.warning(f"Còn {len(unanswered)} câu chưa trả lời: {', '.join(map(str, unanswered))}")
        else:
            st.success("Bạn đã trả lời đầy đủ tất cả các câu.")

        st.markdown("---")

        for i, q in enumerate(questions):
            st.subheader(f"Câu {i+1}: {q['question']}")
            st.radio(
                "Chọn đáp án:",
                options=q["options"],
                key=f"q_{i}",
                index=None
            )
            st.markdown("---")

        submit_disabled = len(unanswered) > 0
        if st.button("Nộp bài", disabled=submit_disabled):
            submit_exam(questions, auto=False)

        if submit_disabled:
            st.caption("Bạn phải trả lời hết tất cả các câu mới nộp được.")

# ===== MAN HINH KET QUA =====
elif st.session_state.screen == "result":
    st.title("✅ Kết quả bài làm")
    st.write(f"**Họ tên:** {st.session_state.name}")
    if st.session_state.lop:
        st.write(f"**Lớp:** {st.session_state.lop}")

    if st.session_state.auto_submitted:
        st.warning("Hết giờ, hệ thống đã tự nộp bài.")
    else:
        st.success("Bạn đã nộp bài thành công.")

    st.subheader(f"Điểm số: {st.session_state.score}/{total_questions}")
    st.markdown("---")

    for i, q in enumerate(questions):
        user_answer = st.session_state.get(f"q_{i}")
        correct_answer = q["answer"]

        st.markdown(f"**Câu {i+1}: {q['question']}**")
        st.write(f"- Đáp án của bạn: {user_answer if user_answer else 'Chưa trả lời'}")
        st.write(f"- Đáp án đúng: {correct_answer}")

        if user_answer == correct_answer:
            st.success("Đúng")
        else:
            st.error("Sai")

        st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Về lịch sử thi"):
            st.session_state.screen = "history"
            st.rerun()

    with col2:
        if st.button("Làm bài mới"):
            reset_exam(total_questions)
            st.rerun()

# ===== MAN HINH LICH SU =====
elif st.session_state.screen == "history":
    st.title("📚 Lịch sử thi")

    history = load_history()

    if not history:
        st.info("Chưa có lịch sử thi nào.")
    else:
        st.write(f"Tổng số lượt thi: **{len(history)}**")
        st.markdown("---")

        for idx, item in enumerate(history, start=1):
            title = f"Lần {idx} - {item['name']} - {item['score']}/{item['total']} - {item['submitted_at']}"
            with st.expander(title):
                st.write(f"**Họ tên:** {item['name']}")
                if item.get("lop"):
                    st.write(f"**Lớp:** {item['lop']}")
                st.write(f"**Thời gian nộp:** {item['submitted_at']}")
                st.write(f"**Điểm:** {item['score']}/{item['total']}")
                st.write(f"**Hình thức nộp:** {'Tự động do hết giờ' if item.get('auto_submitted') else 'Người dùng bấm nộp'}")

                st.markdown("---")
                st.write("**Chi tiết bài làm:**")

                for ans in item["answers"]:
                    st.markdown(f"**Câu {ans['question_no']}: {ans['question']}**")
                    st.write(f"- Đáp án đã chọn: {ans['user_answer'] if ans['user_answer'] else 'Chưa trả lời'}")
                    st.write(f"- Đáp án đúng: {ans['correct_answer']}")
                    if ans["is_correct"]:
                        st.success("Đúng")
                    else:
                        st.error("Sai")
                    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Quay lại trang chào"):
            st.session_state.screen = "welcome"
            st.rerun()

    with col2:
        if st.button("Làm bài mới từ lịch sử"):
            reset_exam(total_questions)
            st.rerun()
