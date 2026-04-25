import gradio as gr
from .core import chat
from .services import APIService


CUSTOM_CSS = """
#chatbot {
    height: 600px;
}
.workflow-container {
    border-left: 4px solid #2196F3;
    padding: 15px;
    border-radius: 4px;
    background: #f5f5f5;
}
"""


def create_interface():
    """Gradio 챗봇 인터페이스 생성 - Gemini + LangGraph 통합"""

    api_service = APIService()
    current_session = {"id": None}  # 현재 세션 ID 저장

    # CSS 스타일링
    css = """
    #chatbot {
        height: 600px;
    }
    .workflow-container {
        border-left: 4px solid #2196F3;
        padding: 15px;
        border-radius: 4px;
        background: #f5f5f5;
    }
    """

    with gr.Blocks(title="Architect Team ChatBot") as demo:
        gr.Markdown("# 🤖 Architect Team ChatBot")
        gr.Markdown("🔗 Gemini API 연동 + 📊 LangGraph 워크플로우 추적")

        with gr.Tabs():
            # 탭 1: 챗봇 메인 (AI 연동)
            with gr.TabItem("💬 Chat with Gemini"):
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("### 💬 AI 채팅")
                        chatbot = gr.Chatbot(
                            label="Chat History",
                            elem_id="chatbot",
                            height=400
                        )

                        with gr.Row():
                            msg = gr.Textbox(
                                label="Message",
                                placeholder="메시지를 입력하세요...",
                                lines=2
                            )
                            submit_btn = gr.Button("Send", variant="primary", scale=1)

                        clear_btn = gr.Button("Clear History")

                    with gr.Column(scale=1):
                        gr.Markdown("### ⚙️ AI 설정")
                        
                        provider_dropdown = gr.Dropdown(
                            choices=api_service.list_available_providers(),
                            label="AI 제공자",
                            value="gemini"
                        )
                        
                        select_provider_btn = gr.Button("🔌 제공자 연결", variant="primary")
                        provider_status = gr.Textbox(
                            label="상태",
                            interactive=False,
                            lines=2
                        )

                # 제공자 연결 핸들러
                def connect_provider(provider):
                    result = api_service.select_provider(provider)
                    if result['success']:
                        return f"✅ {result['message']}"
                    else:
                        return f"❌ {result['message']}"

                select_provider_btn.click(
                    connect_provider,
                    inputs=[provider_dropdown],
                    outputs=[provider_status]
                )

                # AI 응답 핸들러 (워크플로우 추적)
                def chat_with_ai(message, history, provider):
                    if not message:
                        return "", history

                    # 사용자 메시지 추가
                    history = history + [{"role": "user", "content": message}]

                    # Gemini API 호출 (워크플로우 추적)
                    result = api_service.call_api_with_workflow(message, provider)

                    if result['success']:
                        response = result['response']
                        current_session["id"] = result['session_id']
                    else:
                        response = f"❌ 오류: {result['message']}"

                    # 봇 응답 추가
                    history = history + [{"role": "assistant", "content": response}]

                    return "", history

                # 이벤트 핸들러
                msg.submit(
                    chat_with_ai,
                    inputs=[msg, chatbot, provider_dropdown],
                    outputs=[msg, chatbot],
                    queue=False
                )
                submit_btn.click(
                    chat_with_ai,
                    inputs=[msg, chatbot, provider_dropdown],
                    outputs=[msg, chatbot],
                    queue=False
                )
                clear_btn.click(lambda: [], None, chatbot, queue=False)

            # 탭 2: API 키 관리
            with gr.TabItem("🔐 API Settings"):
                gr.Markdown("### API 키 관리 (보안)")
                gr.Markdown("""
                - 🔒 모든 API 키는 **로컬에서 암호화**되어 저장됩니다
                - 📁 Git에는 **SOPS로 암호화**되어 관리됩니다
                - ⚠️ 절대 평문으로 저장되지 않습니다
                """)

                with gr.Row():
                    provider_select = gr.Dropdown(
                        choices=api_service.list_available_providers(),
                        label="AI 제공자 선택",
                        value="gemini"
                    )

                with gr.Row():
                    with gr.Column(scale=3):
                        api_key_input = gr.Textbox(
                            label="API Key",
                            placeholder="여기에 API 키를 입력하세요",
                            type="password"
                        )
                    with gr.Column(scale=1):
                        save_key_btn = gr.Button("💾 Save", variant="primary")

                with gr.Row():
                    status_output = gr.Textbox(
                        label="상태",
                        interactive=False,
                        lines=3
                    )

                # 제공자 선택 핸들러
                def on_provider_select(provider):
                    existing_key = api_service.config.get_api_key(provider, from_env=False)
                    if existing_key:
                        return f"✅ {provider}의 API 키가 저장되어 있습니다."
                    else:
                        return f"❌ {provider}의 API 키가 저장되지 않았습니다."

                provider_select.change(
                    on_provider_select,
                    inputs=[provider_select],
                    outputs=[status_output]
                )

                # API 키 저장 핸들러
                def save_api_key(provider, api_key):
                    if not api_key:
                        return "⚠️ API 키를 입력해주세요."
                    
                    result = api_service.set_api_key(provider, api_key)
                    if result['success']:
                        return f"✅ {result['message']}\n\n🔒 로컬 암호화 저장됨"
                    else:
                        return f"❌ {result['message']}"

                save_key_btn.click(
                    save_api_key,
                    inputs=[provider_select, api_key_input],
                    outputs=[status_output]
                )

                # 구분선
                gr.Markdown("---")

                # 설정된 제공자 목록
                gr.Markdown("### 📋 설정된 AI 제공자")
                
                def get_configured_status():
                    configured = api_service.get_configured_providers()
                    if not configured:
                        return "아직 설정된 AI 제공자가 없습니다."
                    return "설정된 제공자:\n" + "\n".join([f"✅ {p}" for p in configured])

                status_info = gr.Textbox(
                    value=get_configured_status(),
                    interactive=False,
                    lines=3
                )

                # 상태 갱신 버튼
                refresh_btn = gr.Button("🔄 상태 갱신")
                refresh_btn.click(
                    lambda: get_configured_status(),
                    outputs=[status_info]
                )

            # 탭 3: 워크플로우 시각화 (NEW)
            with gr.TabItem("📊 Workflow Monitor"):
                gr.Markdown("### 📊 LangGraph 워크플로우 추적")
                gr.Markdown("""
                마지막 AI 호출의 워크플로우를 모니터링합니다:
                - 🔵 각 단계별 실행 상태
                - ⏱️ 타임스탬프
                - ❌ 오류 메시지 (발생 시)
                - 📈 진행률
                """)

                with gr.Row():
                    refresh_workflow_btn = gr.Button("🔄 워크플로우 갱신", variant="primary")

                # 워크플로우 HTML 시각화
                workflow_html = gr.HTML(
                    value="<div style='padding: 20px; color: #999;'>아직 워크플로우 데이터가 없습니다.</div>"
                )

                # 워크플로우 JSON 데이터
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 📋 워크플로우 상세 정보")
                        workflow_details = gr.JSON(
                            value={},
                            label="Workflow JSON"
                        )

                # 워크플로우 갱신 핸들러
                def refresh_workflow():
                    session_id = current_session.get("id")
                    if not session_id:
                        return (
                            "<div style='padding: 20px; color: #F44336;'>아직 AI 호출이 없습니다. 먼저 메시지를 전송해주세요.</div>",
                            {}
                        )
                    
                    html_timeline = api_service.get_workflow_html(session_id)
                    workflow_json = api_service.get_workflow(session_id)
                    
                    return html_timeline, workflow_json

                refresh_workflow_btn.click(
                    refresh_workflow,
                    outputs=[workflow_html, workflow_details]
                )

            # 탭 4: 정보
            with gr.TabItem("ℹ️ Info"):
                gr.Markdown("""
                ### 🔐 보안 + 🤖 AI 통합 아키텍처
                
                #### 🔗 Gemini API 연동
                - **실시간 연동**: LangChain + Google Generative AI
                - **토큰 제한**: API 키 별도 관리로 안전
                - **응답 캐시**: 성능 최적화
                
                #### 📊 LangGraph 워크플로우
                - **상태 추적**: 각 단계별 실행 상태 기록
                - **오류 처리**: 실패 시점 즉시 감지
                - **타임스탬프**: 실행 시간 추적
                - **메타데이터**: 응답 크기, 모델 정보 등
                
                #### 🔐 보안 계층
                1. **로컬 암호화**: Fernet AES-128
                2. **파일 암호화**: SOPS (배포 시)
                3. **환경변수**: .env 분리
                
                #### 📈 워크플로우 노드
                ```
                INPUT → VALIDATE → API_CALL → PROCESS → OUTPUT
                   ↓        ↓          ↓         ↓        ↓
                사용자  API검증   Gemini호출  텍스트정제  응답반환
                ```
                
                #### 🛠️ 기술 스택
                - **UI**: Gradio 6.13+
                - **LLM**: Google Generative AI (Gemini Pro)
                - **워크플로우**: LangGraph
                - **보안**: Cryptography + SOPS
                - **테스트**: Pytest
                """)

    return demo
