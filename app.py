import os
from dotenv import load_dotenv
from chatbot.ui import CUSTOM_CSS, create_interface


if __name__ == "__main__":
    load_dotenv()

    # 환경 변수에서 호스트와 포트 설정
    host = os.getenv("GRADIO_HOST", "0.0.0.0")
    port = int(os.getenv("GRADIO_PORT", 7860))
    share = os.getenv("GRADIO_SHARE", "false").lower() == "true"

    app = create_interface()
    app.launch(
        server_name=host,
        server_port=port,
        share=share,
        show_error=True,
        debug=True,
        # Gradio 6.0에서 css를 launch()로 이동
        css=CUSTOM_CSS
    )
