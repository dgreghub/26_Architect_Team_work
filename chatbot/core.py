from datetime import datetime


def chat(message, history):
    """
    Gradio 챗봇 응답 함수
    - message: 사용자의 메시지
    - history: 대화 이력 (list of dicts)
    """
    if not message:
        return "", history

    # 기본 응답
    response = "안녕하세요 8팀 봇입니다."

    # Gradio Chatbot이 기대하는 형식으로 history 업데이트
    # 새로운 버전에서는 list of dicts 형식을 사용
    new_history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": response}
    ]

    return "", new_history