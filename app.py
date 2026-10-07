import json
import os
from google import genai
from google.genai import types
import streamlit as st

# 1. 페이지 기본 세팅
st.set_page_config(
    page_title="AI 백운도사 - 신통한 사주/운세", page_icon="🔮", layout="centered"
)

# 동양풍 모던 디자인 CSS
st.markdown(
    """
    <style>
    .main {
        background-color: #fdfbf7;
    }
    .stButton>button {
        width: 100%;
        background-color: #8b0000;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        padding: 12px;
    }
    .stButton>button:hover {
        background-color: #a00000;
        color: white;
    }
    .result-card {
        background-color: #ffffff;
        border: 2px solid #d4af37;
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 2px 2px 12px rgba(0,0,0,0.08);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 2. API 키 불러오기 (Local or Streamlit Secrets)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = st.text_input(
            "Gemini API Key를 입력하세요", type="password"
        )

# 3. 타이틀 영역
st.title("🔮 AI 백운도사의 신통한 사주 풀이")
st.caption(
    "40년 명리학 고수 AI 백운도사가 당신의 사주팔자와 운명을 명쾌하게 풀어드립니다."
)
st.divider()

# 4. 입력 폼 (사용자 정보 수집)
with st.form("saju_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("성함 (또는 닉네임)", placeholder="이창현")
        gender = st.radio("성별", ["남성", "여성"], horizontal=True)
    with col2:
        birth_date = st.date_input("생년월일")
        calendar_type = st.radio(
            "양력/음력", ["양력", "음력"], horizontal=True
        )

    col3, col4 = st.columns(2)
    with col3:
        birth_time = st.selectbox(
            "태어난 시 (모르면 태어난 시 모름 선택)",
            [
                "태어난 시 모름",
                "자시 (23:30~01:29)",
                "축시 (01:30~03:29)",
                "인시 (03:30~05:29)",
                "묘시 (05:30~07:29)",
                "진시 (07:30~09:29)",
                "사시 (09:30~11:29)",
                "오시 (11:30~13:29)",
                "미시 (13:30~15:29)",
                "신시 (15:30~17:29)",
                "유시 (17:30~19:29)",
                "술시 (19:30~21:29)",
                "해시 (21:30~23:29)",
            ],
        )
    with col4:
        worry_category = st.selectbox(
            "오늘의 핵심 고민",
            [
                "💼 취업/진로 및 승진운",
                "💖 연애/궁합 및 결혼운",
                "💰 재물운 및 투자/주식",
                "🩺 올해 전체적인 총운 및 건강",
            ],
        )

    specific_worry = st.text_area(
        "구체적인 고민 (선택사항)",
        placeholder="예: 올해 하반기 대기업 서류 합격 기운이 있을까요? / 지금 만나는 사람과 계속 가도 될까요?",
    )

    submit_button = st.form_submit_button("🔮 복채 넣고 점괘 보기 (무료)")

# 5. Gemini 사주 분석 로직
SAJU_SYSTEM_PROMPT = """
너는 40년 경력의 신통하기로 소문난 사주명리학자이자 인생 멘토인 'AI 백운도사'다.
사용자의 생년월일시와 고민을 바탕으로 사주팔자의 오행(木, 火, 土, 金, 水) 기운과 운세를 명쾌하게 분석하라.

[말투/톤앤매너]
- 신비로우면서도 권위 있고 따뜻한 도사 말투(~하느니라, ~이로다, ~해보거라).
- 뜬구름 잡는 소리 말고 직설적이고 명확한 조언을 줄 것.

[출력 규격 (JSON만 출력)]
{
  "summary": "한 줄 총평 (예: 불의 기운이 강하여 열정적이나 결실을 맺는 금의 기운을 보강해야 할 사주로다)",
  "five_elements": "오행 분석 및 강한 기운/부족한 기운 설명",
  "worry_answer": "고민에 대한 명쾌한 운세 풀이 및 대운 시기",
  "lucky": {
    "color": "행운의 색",
    "number": "행운의 숫자",
    "direction": "행운의 방위"
  },
  "dosa_advice": "백운도사의 3줄 인생 처방전",
  "premium_preview": "심층 분석 미리보기 (결제를 유도할 만한 매력적인 1줄 예고)"
}
"""

if submit_button:
    if not api_key:
        st.error("Gemini API Key를 먼저 설정해라!")
    elif not name:
        st.warning("성함을 입력해 주세요!")
    else:
        with st.spinner(
            "🔮 백운도사가 만세력을 펼치고 천기를 읽는 중입니다..."
        ):
            user_info = f"""
            - 이름: {name} ({gender})
            - 생년월일: {birth_date} ({calendar_type})
            - 태어난 시: {birth_time}
            - 고민 카테고리: {worry_category}
            - 구체적 고민: {specific_worry if specific_worry else '없음'}
            """

            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        SAJU_SYSTEM_PROMPT,
                        f"사용자 사주 정보:\n{user_info}",
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.7,
                    ),
                )

                data = json.loads(response.text)

                # 결과 출력
                st.balloons()
                st.markdown(
                    f"""
                <div class="result-card">
                    <h2>📜 {name} 님의 사주 점괘</h2>
                    <p style="font-size: 18px; font-weight: bold; color: #8b0000;">"{data['summary']}"</p>
                    <hr>
                    <h4>☯️ 오행(五行) 기운 분석</h4>
                    <p>{data['five_elements']}</p>
                    <h4>🎯 {worry_category} 심층 풀이</h4>
                    <p>{data['worry_answer']}</p>
                    <h4>🍀 행운의 처방</h4>
                    <ul>
                        <li><b>행운의 색:</b> {data['lucky']['color']}</li>
                        <li><b>행운의 숫자:</b> {data['lucky']['number']}</li>
                        <li><b>행운의 방향:</b> {data['lucky']['direction']}</li>
                    </ul>
                    <h4>💡 백운도사의 인생 처방전</h4>
                    <p style="background-color: #f0f0f0; padding: 10px; border-radius: 8px;">{data['dosa_advice']}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # 수익화(결제 유도) 영역
                st.divider()
                st.warning(f"🔒 **[프리미엄 1:1 궁합/상세 월별 운세]**")
                st.write(
                    f"👉 **도사님의 비기 미리보기:** {data.get('premium_preview', '올해 가장 결정적인 대운이 들어오는 달은 따로 있느니라...')}"
                )

                if st.button("💳 복채 1,900원 내고 2026년 월별 상세 운세 열람하기"):
                    st.info(
                        "💡 (수익화 모듈 연결 예정) 토스페이먼츠/카카오페이 결제창이 뜨는 공간입니다!"
                    )

            except Exception as e:
                st.error(f"점괘를 읽는 중 오류가 발생했습니다: {e}")