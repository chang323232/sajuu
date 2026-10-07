import json
import os
import datetime
from google import genai
from google.genai import types
import streamlit as st

# 1. 페이지 기본 세팅
st.set_page_config(
    page_title="AI 백운도사 - 신통한 운세", page_icon="🌙", layout="centered"
)

# 2. 여심/MZ 저격 신비로운 타로 감성 CSS
st.markdown(
    """
    <style>
    /* 전체 배경: 신비로운 딥 퍼플 그라데이션 */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }
    /* 기본 텍스트 색상 */
    html, body, [class*="css"] {
        color: #f0e6d2 !important;
    }
    h1, h2, h3, h4, p, span, label {
        color: #f0e6d2 !important;
    }
    /* 입력폼 스타일 커스텀 */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea, .stDateInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(212, 175, 55, 0.5) !important;
        border-radius: 8px;
    }
    /* 복채 버튼: 금박 부적 감성 */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #d4af37, #ffdf73, #d4af37);
        color: #1a0b2e !important;
        font-size: 20px;
        font-weight: 900;
        border-radius: 12px;
        border: none;
        padding: 15px;
        box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0px 6px 20px rgba(212, 175, 55, 0.6);
    }
    /* 결과 카드: 반투명 유리 스타일 */
    .result-card {
        background: rgba(20, 15, 40, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(212, 175, 55, 0.4);
        border-radius: 15px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    }
    .result-card h2, .result-card h4 {
        color: #ffdf73 !important;
    }
    .result-card p, .result-card li {
        color: #fdfbf7 !important;
        line-height: 1.6;
    }
    hr {
        border-color: rgba(212, 175, 55, 0.3);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 3. API 키 불러오기
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = st.text_input("Gemini API Key를 입력하세요", type="password")

# 4. 타이틀 영역
st.title("🌙 AI 백운도사의 신통한 사주 풀이")
st.caption("천기를 읽는 40년 명리학 고수, 당신의 운명과 은밀한 고민을 꿰뚫어 봅니다.")
st.divider()

# 5. 입력 폼 (사용자 정보 수집)
with st.form("saju_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("성함 (또는 닉네임)", placeholder="김철수")
        gender = st.radio("성별", ["남성", "여성"], horizontal=True)
    with col2:
        # 생년월일 범위를 1900년~2100년으로 확장
        birth_date = st.date_input(
            "생년월일",
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date(2100, 12, 31),
            value=datetime.date(1995, 1, 1) # 기본 세팅 날짜
        )
        calendar_type = st.radio("양력/음력", ["양력", "음력"], horizontal=True)

    birth_time =
