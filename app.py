import json
import os
from google import genai
from google.genai import types
import streamlit as st

# 1. 페이지 기본 세팅
st.set_page_config(
    page_title="AI 백운도사 - 신통한 운세", page_icon="🌙", layout="centered"
)

# 2. 가독성 최고! 밝고 세련된 연보라/아이보리 타로 감성 CSS
st.markdown(
    """
    <style>
    /* 전체 배경: 밝고 신비로운 톤 */
    .stApp {
        background: linear-gradient(135deg, #f5f0fa, #fdfbf7);
    }
    /* 기본 텍스트 색상: 깔끔한 검은색 */
    html, body, [class*="css"] {
        color: #111111 !important;
    }
    h1, h2, h3, h4, p, span, label {
        color: #111111 !important;
    }
    /* 입력폼 스타일 커스텀 */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea, .stDateInput>div>div>input {
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 1px solid #dcd1e3 !important;
        border-radius: 8px;
    }
    /* 복채 버튼: 고급스러운 딥 퍼플 */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #4b3e7c, #302b63);
        color: #ffffff !important;
        font-size: 20px;
        font-weight: 900;
        border-radius: 12px;
        border: none;
        padding: 15px;
        box-shadow: 0px 4px 15px rgba(48, 43, 99, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0px 6px 20px rgba(48, 43, 99, 0.4);
    }
    /* 결과 카드: 깔끔한 화이트 */
    .result-card {
        background: #ffffff;
        border: 1px solid #e2dce8;
        border-radius: 15px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
    }
    .result-card h2, .result-card h4 {
        color: #111111 !important;
    }
    .result-card p, .result-card li {
        color: #333333 !important;
        line-height: 1.6;
    }
    hr {
        border-color: #e2dce8;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 3. API 키 불러오기 (데이터베이스 저장 기능 없음!)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = st.text_input("Gemini API Key를 입력하세요", type="password")

# 4. 타이틀 영역
st.title("🌙 AI 백운도사의 신통한 사주 풀이")
st.caption("천기를 읽는 40년 명리학 고수, 당신의 운명과 은밀한 고민을 꿰뚫어 봅니다. (※ 입력된 정보는 절대 저장되지 않습니다)")
st.divider()

# 5. 입력 폼 (사용자 정보 수집 - 달력 위젯 대신 드롭다운으로 교체)
with st.form("saju_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("성함 (또는 닉네임)", placeholder="김철수")
        gender = st.radio("성별", ["남성", "여성"], horizontal=True)
        calendar_type = st.radio("양력/음력", ["양력", "음력"], horizontal=True)

    with col2:
        st.markdown("<p style='font-size:14px; margin-bottom:5px; font-weight:600;'>생년월일</p>", unsafe_allow_html=True)
        
        # 1930년~2026년 드롭다운 (기본값 1995년)
        col_y, col_m, col_d = st.columns(3)
        with col_y:
            b_year = st.selectbox("연도", list(range(1930, 2027)), index=65, label_visibility="collapsed")
        with col_m:
            b_month = st.selectbox("월", list(range(1, 13)), label_visibility="collapsed")
        with col_d:
            b_day = st.selectbox("일", list(range(1, 32)), label_visibility="collapsed")

        birth_time = st.selectbox(
            "태어난 시",
            [
                "모름 (태어난 시 모름)", "자시 (23:30~01:29)", "축시 (01:30~03:29)",
                "인시 (03:30~05:29)", "묘시 (05:30~07:29)", "진시 (07:30~09:29)",
                "사시 (09:30~11:29)", "오시 (11:30~13:29)", "미시 (13:30~15:29)",
                "신시 (15:30~17:29)", "유시 (17:30~19:29)", "술시 (19:30~21:29)",
                "해시 (21:30~23:29)",
            ],
        )

    worry = st.text_area(
        "도사님께 털어놓을 당신의 깊은 고민",
        placeholder="예: 올해 하반기 이직운이 들어와 있나요? / 요즘 만나는 사람과 계속 가도 될까요? / 왜 이렇게 돈이 안 모이는지 답답합니다.",
        height=100
    )

    submit_button = st.form_submit_button("🔮 천기누설 점괘 보기 (무료)")

# 6. Gemini 사주 분석 로직
SAJU_SYSTEM_PROMPT = """
너는 40년 경력의 신통하기로 소문난 사주명리학자이자 인생 멘토인 'AI 백운도사'다.
사용자의 생년월일시와 털어놓은 고민을 바탕으로 사주팔자의 기운을 명쾌하고 뼈때리게 분석하라.

[말투/톤앤매너]
- 신비로우면서도 권위 있고 따뜻한 도사 말투(~하느니라, ~이로다, ~해보거라).
- 뻔하고 막연한 소리 금지. 직설적이고 구체적인 시기나 행동 방향을 제시할 것.

[출력 규격 (JSON만 출력)]
{
  "summary": "한 줄 총평 (예: 겉으로는 강한 불꽃이나 속은 여린 촛불과 같아 사람에게 상처를 조심해야 할 사주로다.)",
  "five_elements": "오행 분석 및 강한 기운/부족한 기운 설명",
  "worry_answer": "사용자가 털어놓은 '고민'에 대한 명쾌한 운세 풀이 및 대운 시기",
  "lucky": {
    "color": "행운의 색",
    "number": "행운의 숫자",
    "direction": "행운의 방위 및 장소"
  },
  "dosa_advice": "백운도사의 3줄 인생 처방전",
  "premium_preview": "심층 분석 미리보기 (결제를 유도할 만한 소름 돋는 1줄 예고)"
}
"""

if submit_button:
    if not api_key:
        st.error("Gemini API Key를 먼저 설정해주세요.")
    elif not name:
        st.warning("성함을 입력해 주셔야 명부를 뒤져 운명을 봅니다.")
    elif not worry:
        st.warning("어떤 점이 답답한지 고민을 적어주셔야 도사님이 꿰뚫어 봅니다.")
    else:
        with st.spinner("🔮 백운도사가 만세력을 펼치고 당신의 천기를 읽는 중입니다..."):
            user_info = f"""
            - 이름: {name} ({gender})
            - 생년월일: {b_year}년 {b_month}월 {b_day}일 ({calendar_type})
            - 태어난 시: {birth_time}
            - 고민: {worry}
            """

            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
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

                st.balloons()
                st.markdown(
                    f"""
                <div class="result-card">
                    <h2>📜 {name} 님의 사주 점괘</h2>
                    <p style="font-size: 20px; font-weight: bold; color: #111111 !important;">"{data['summary']}"</p>
                    <hr>
                    <h4>☯️ 오행(五行) 기운 분석</h4>
                    <p>{data['five_elements']}</p>
                    <br>
                    <h4>🎯 도사님의 명쾌한 해답</h4>
                    <p>{data['worry_answer']}</p>
                    <br>
                    <h4>🍀 기운을 보강해 줄 행운의 처방</h4>
                    <ul>
                        <li><b>행운의 색:</b> {data['lucky']['color']}</li>
                        <li><b>행운의 숫자:</b> {data['lucky']['number']}</li>
                        <li><b>행운의 방향:</b> {data['lucky']['direction']}</li>
                    </ul>
                    <br>
                    <h4>💡 백운도사의 인생 처방전</h4>
                    <p style="background: rgba(0, 0, 0, 0.05); padding: 15px; border-radius: 8px; color: #111111 !important;">{data['dosa_advice']}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                st.divider()
                st.warning("🔒 **[프리미엄 심층 운세 및 궁합 풀이]**")
                st.write(
                    f"👉 **도사님의 비기 미리보기:** {data.get('premium_preview', '올해 당신 인생을 바꿀 결정적인 귀인이 나타나는 달은 따로 있느니라...')}"
                )

                if st.button("💳 복채 1,900원 내고 남은 인생 대운 열람하기"):
                    st.info("💡 (수익화 모듈 연결 예정) 토스페이먼츠/카카오페이 결제창이 뜰 예정입니다!")

            except Exception as e:
                st.error(f"점괘를 읽는 중 기운이 흩어졌습니다 (에러 발생): {e}")
