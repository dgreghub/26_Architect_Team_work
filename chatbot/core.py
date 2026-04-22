from datetime import datetime


def chat(message, history):
    """
    Gradio 챗봇 응답 함수
    - message: 사용자의 메시지
    - history: 대화 이력
    """
    if not message:
        return ""

    # 간단한 응답 로직 (실제로는 LLM API 호출 등으로 확장 가능)
    response = f"[{datetime.now().strftime('%H:%M:%S')}] 사용자님이 보낸 메시지를 받았습니다: '{message}'"

    return response