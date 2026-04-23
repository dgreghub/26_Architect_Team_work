import gradio as gr
from .core import chat


def create_interface():
    """Gradio 챗봇 인터페이스 생성"""

    # CSS 스타일링
    css = """
    #chatbot {
        height: 600px;
    }
    """

    with gr.Blocks(title="Architect Team ChatBot") as demo:
        gr.Markdown("# 🤖 Architect Team ChatBot")
        gr.Markdown("GCP 기반 8팀 챗봇 애플리케이션입니다.")

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ChatBot")
                chatbot = gr.Chatbot(
                    label="Chat History",
                    elem_id="chatbot",
                    height=400,
                    type="messages"  # 새로운 메시지 형식 사용
                )

                with gr.Row():
                    msg = gr.Textbox(
                        label="Message",
                        placeholder="메시지를 입력하세요...",
                        lines=2
                    )
                    submit_btn = gr.Button("Send", variant="primary")

                clear_btn = gr.Button("Clear History")

        # 이벤트 핸들러
        msg.submit(chat, inputs=[msg, chatbot], outputs=[msg, chatbot], queue=False)
        submit_btn.click(chat, inputs=[msg, chatbot], outputs=[msg, chatbot], queue=False)
        clear_btn.click(lambda: None, None, chatbot, queue=False)

    return demo
