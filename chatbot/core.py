from datetime import datetime


def chat(message, history):
    """
    Gradio 챗봇 응답 함수
    - message: 사용자의 메시지
    - history: 대화 이력 (list of [user, bot] pairs)
    """
    if not message:
        return "", history

    # 기본 응답
    response = "안녕하세요 8팀 봇입니다."

    # Gradio Chatbot 형식: [[user_msg, bot_msg], ...]
    new_history = history + [[message, response]]

    # 메시지 입력창 초기화 및 히스토리 반환
    return "", new_history