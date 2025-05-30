import streamlit as st
import requests
import json

# 페이지 기본 설정
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖",
    layout="wide"
)

# 제목 설정
st.title("🤖 Gemini AI Chatbot")
st.markdown("---")

# API 키 설정
try:
    # .streamlit/secrets.toml 파일에서 API 키 로드
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception as e:
    st.error("API 키를 설정해주세요! (.streamlit/secrets.toml 파일에 GOOGLE_API_KEY를 설정해주세요)")
    st.stop()

# Gemini API 설정
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def get_gemini_response(messages):
    """
    Gemini API를 호출하여 응답을 받아오는 함수
    :param messages: 이전 대화 내역을 포함한 메시지 리스트
    :return: API 응답 텍스트
    """
    try:
        # 대화 내역을 API 요청 형식으로 변환
        conversation = []
        for msg in messages:
            conversation.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [{"text": msg["content"]}]
            })

        # API 요청 데이터 구성
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GOOGLE_API_KEY
        }
        
        data = {
            "contents": conversation,
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }

        # API 호출
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()  # HTTP 에러 체크
        
        # 응답 처리
        response_data = response.json()
        if "candidates" in response_data and len(response_data["candidates"]) > 0:
            return response_data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "죄송합니다. 응답을 생성하는데 문제가 발생했습니다."

    except requests.exceptions.RequestException as e:
        st.error(f"API 호출 중 오류가 발생했습니다: {str(e)}")
        return None
    except Exception as e:
        st.error(f"예상치 못한 오류가 발생했습니다: {str(e)}")
        return None

# 세션 상태 초기화 (대화 내역 저장용)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 내역 표시
st.markdown("### 대화 내역")
for message in st.session_state.messages:
    if message["role"] == "user":
        st.write("👤 사용자: " + message["content"])
    else:  # assistant
        st.write("🤖 Gemini: " + message["content"])

# 사용자 입력 UI
user_input = st.text_area("메시지를 입력하세요:", height=100)

# 전송 버튼을 컬럼을 사용하여 가운데 정렬
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("전송"):
        if not user_input:
            st.warning("메시지를 입력해주세요!")
            st.stop()
        
        # 사용자 메시지를 대화 내역에 추가
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # 로딩 표시
        with st.spinner('Gemini AI가 응답을 생성하고 있습니다...'):
            # Gemini API 호출
            response = get_gemini_response(st.session_state.messages)
            
            if response:
                # 응답을 대화 내역에 추가
                st.session_state.messages.append({"role": "assistant", "content": response})
                # 페이지 새로고침
                st.experimental_rerun()
