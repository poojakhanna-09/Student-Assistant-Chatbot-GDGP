import json
import re
from pathlib import Path

import streamlit as st

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Student Assistant | GDGP",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- LOAD DATA --------------------
try:
    with open("data/college_data.json", "r", encoding="utf-8") as file:
        college_data = json.load(file)
    college_name = college_data["college_info"]["name"]
except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
    st.error(f"Unable to load college data: {e}")
    st.stop()

# -------------------- TEXT NORMALIZATION --------------------
STOP_WORDS = {
    "what", "is", "are", "the", "a", "an", "of", "in", "at", "to", "for",
    "how", "can", "i", "do", "does", "it", "my", "me", "please", "tell",
    "about", "and", "or", "on", "with", "there", "this", "that", "be", "have",
    "has", "from", "your", "you", "we", "our", "college", "kindly"
}


def normalize_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    words = []
    for word in text.split():
        if word.endswith("ies") and len(word) > 4:
            word = word[:-3] + "y"
        elif word.endswith("es") and len(word) > 4:
            word = word[:-2]
        elif word.endswith("s") and len(word) > 3:
            word = word[:-1]
        words.append(word)
    return " ".join(words)


def get_useful_words(text):
    return {word for word in normalize_text(text).split() if word not in STOP_WORDS and len(word) > 1}

# -------------------- CHATBOT RESPONSE --------------------
def get_response(user_input):
    question = normalize_text(user_input)
    user_words = get_useful_words(user_input)
    if not question:
        return "Please enter a question so I can help you."

    greetings = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
    if question in greetings:
        return f"Hello! 👋 Welcome to {college_name} Student Assistant. How can I help you today?"

    if question in {"thank you", "thanks", "thank", "thx"}:
        return "You're welcome! 😊 Feel free to ask me anything about the college."

    if question in {"bye", "goodbye", "see you", "see you later"}:
        return "Goodbye! 👋 Have a great day!"

    if "college name" in question or "name of college" in question or "which college" in question:
        return f"The college name is {college_name}."

    best_response = None
    best_score = 0
    for category in college_data.get("categories", []):
        for entry in category.get("entries", []):
            candidates = list(entry.get("keywords", []))
            if entry.get("question"):
                candidates.append(entry["question"])
            for candidate in candidates:
                candidate = str(candidate)
                candidate_normalized = normalize_text(candidate)
                candidate_words = get_useful_words(candidate)
                if candidate_normalized and candidate_normalized in question:
                    return entry.get("answer", entry.get("response", "I couldn't find an answer."))
                if not user_words or not candidate_words:
                    continue
                common_words = user_words.intersection(candidate_words)
                score = (0.7 * len(common_words) / len(candidate_words)) + (0.3 * len(common_words) / len(user_words))
                if score > best_score:
                    best_score = score
                    best_response = entry.get("answer", entry.get("response", "I couldn't find an answer."))
    if best_score >= 0.50 and best_response:
        return best_response
    return (
        "Sorry, I couldn't find a proper answer to your question. 😕 Try asking about admissions, courses, fees, exams, facilities or other college-related information."
    )

# -------------------- CUSTOM DESIGN --------------------
st.markdown("""
<style>
/* Full-page background */
.stApp {
    background: linear-gradient(135deg, #0b1120 0%, #131c36 52%, #172554 100%);
    color: #f1f5f9;
}
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: transparent !important;
}
[data-testid="stMain"] > div {
    background: transparent !important;
}
/* Use the full available width and give the page breathing room */
.block-container {
    max-width: 1400px !important;
    width: 100% !important;
    padding: 2rem 3rem 8rem 3rem !important;
}
/* Text */
h1, h2, h3, p, label { color: #f8fafc !important; }
/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: 1px solid #334155;
}
[data-testid="stSidebar"] p { color: #cbd5e1 !important; }
/* Chat cards */
[data-testid="stChatMessage"] {
    background: rgba(30, 41, 59, 0.88) !important;
    border: 1px solid #334155 !important;
    border-radius: 18px !important;
    padding: 1rem !important;
    margin-bottom: 1rem !important;
}
/* Streamlit's bottom chat dock: avoid the white band */
[data-testid="stBottom"], [data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"], [data-testid="stBottomBlockContainer"] > div {
    background: transparent !important;
}
[data-testid="stChatInput"] {
    background: #111827 !important;
    border: 1px solid #475569 !important;
    border-radius: 16px !important;
}
[data-testid="stChatInput"] textarea { color: #f8fafc !important; }
[data-testid="stChatInput"] textarea::placeholder { color: #94a3b8 !important; }
[data-testid="stChatInput"]:focus-within {
    border-color: #60a5fa !important;
    box-shadow: 0 0 0 1px #60a5fa !important;
}
/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #2563eb, #0891b2) !important;
    color: white !important;
    border: 1px solid transparent !important;
    border-radius: 14px !important;
    min-height: 54px !important;
    font-weight: 600 !important;
    transition: all .2s ease;
}
.stButton > button:hover {
    border: 1px solid #67e8f9 !important;
    transform: translateY(-2px);
}
hr { border-color: #334155 !important; }
/* Logo sizing */
[data-testid="stImage"] img { border-radius: 16px; }
/* Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
@media (max-width: 900px) {
    .block-container { padding: 1.2rem 1rem 7rem 1rem !important; }
}
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("## 🎓 Student Assistant")
    st.divider()
    st.markdown("### 💡 How can I help?")
    st.write("Ask me about admissions, courses, exams, facilities, fees and other college information.")
    st.divider()
    st.markdown("### 🏫 About")
    st.write(college_name)
    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# -------------------- HEADER --------------------
logo_path = Path("data/logo.png")
logo_col, title_col, spacer_col = st.columns([1, 3, 1])
with logo_col:
    if logo_path.exists():
        try:
            st.image(str(logo_path), width=115)
        except Exception:
            st.markdown("🎓")
    else:
        st.markdown("🎓")
with title_col:
    st.markdown("<h1 style='text-align:center; font-size:2.8rem;'>Student Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:1.15rem;'>Your smart college information assistant</p>", unsafe_allow_html=True)
st.divider()

# -------------------- QUICK QUESTIONS --------------------
st.markdown("### ✨ Quick Questions")
quick_questions = [
    "What courses are available?",
    "How can I get admission?",
    "What facilities are available?",
    "How can I check my result?",
]
cols = st.columns(2)
selected_question = None
for i, question in enumerate(quick_questions):
    with cols[i % 2]:
        if st.button(question, key=f"quick_{i}", use_container_width=True):
            selected_question = question

# -------------------- CHAT HISTORY --------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------- USER INPUT --------------------
user_input = st.chat_input("Ask anything about your college...")
if selected_question:
    user_input = selected_question

# -------------------- CHAT PROCESSING --------------------
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    response = get_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
