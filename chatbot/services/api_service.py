"""
통합 AI API 서비스
- API 키 관리
- 제공자 관리
- 워크플로우 추적과 함께 API 호출
"""
import uuid
from typing import Dict, Any

from config import ConfigManager
from chatbot.models import create_provider, PROVIDER_REGISTRY
from chatbot.workflow import (
    WorkflowTracker, ChatbotState, WorkflowNode, 
    NodeType, ExecutionStatus
)


class APIService:
    """통합 AI API 서비스"""

    def __init__(self):
        self.config = ConfigManager()
        self.active_provider = None
        self.current_client = None
        self.workflow_tracker = WorkflowTracker()

    # ======================== 제공자 관리 ========================
    
    def list_available_providers(self) -> list:
        """지원하는 AI 제공자 목록"""
        return list(PROVIDER_REGISTRY.keys())

    def get_configured_providers(self) -> list:
        """현재 설정된 AI 제공자 목록"""
        return self.config.get_configured_providers()

    def set_api_key(self, provider: str, api_key: str) -> dict:
        """API 키 설정"""
        if provider not in self.list_available_providers():
            return {
                'success': False,
                'message': f"지원하지 않는 제공자: {provider}"
            }

        try:
            if self.config.set_api_key(provider, api_key):
                return {
                    'success': True,
                    'message': f"{provider} API 키가 저장되었습니다."
                }
            else:
                return {
                    'success': False,
                    'message': f"{provider} API 키 저장에 실패했습니다."
                }
        except Exception as e:
            return {'success': False, 'message': f"오류: {str(e)}"}

    def select_provider(self, provider: str) -> dict:
        """제공자 선택 및 클라이언트 초기화"""
        api_key = self.config.get_api_key(provider)
        
        if not api_key:
            return {
                'success': False,
                'message': f"{provider}의 API 키가 설정되지 않았습니다."
            }

        try:
            provider_instance = create_provider(provider, api_key)
            
            if not provider_instance.is_available():
                return {
                    'success': False,
                    'message': f"{provider} 라이브러리가 설치되지 않았습니다."
                }
            
            if not provider_instance.initialize():
                return {
                    'success': False,
                    'message': f"{provider} 클라이언트 초기화 실패"
                }
            
            self.active_provider = provider
            self.current_client = provider_instance
            
            return {
                'success': True,
                'message': f"✓ {provider} 제공자가 선택되었습니다.",
                'provider': provider
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"제공자 선택 실패: {str(e)}"
            }

    def remove_api_key(self, provider: str) -> dict:
        """API 키 삭제"""
        try:
            if self.config.remove_api_key(provider):
                if self.active_provider == provider:
                    self.active_provider = None
                    self.current_client = None
                return {
                    'success': True,
                    'message': f"{provider} API 키가 삭제되었습니다."
                }
            else:
                return {
                    'success': False,
                    'message': f"{provider} API 키 삭제에 실패했습니다."
                }
        except Exception as e:
            return {'success': False, 'message': f"오류: {str(e)}"}

    # ======================== API 호출 ========================
    
    def call_api_with_workflow(
        self,
        message: str,
        provider: str = None,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        워크플로우 추적과 함께 API 호출
        """
        target_provider = provider or self.active_provider
        session_id = session_id or str(uuid.uuid4())
        
        if not target_provider:
            return self._error_response(
                "선택된 AI 제공자가 없습니다.",
                session_id
            )

        # 워크플로우 상태 생성
        state = self.workflow_tracker.create_state(session_id, message, target_provider)
        
        try:
            # ① 입력 노드
            state.add_node(WorkflowNode(
                id="input",
                type=NodeType.INPUT,
                name="사용자 입력",
                description=f"메시지: {message[:50]}..." if len(message) > 50 else f"메시지: {message}"
            ))
            state.update_node("input", ExecutionStatus.SUCCESS, {'message': message})
            
            # ② API 키 검증 노드
            state.add_node(WorkflowNode(
                id="validate",
                type=NodeType.PROCESS,
                name="API 키 검증",
                description=f"제공자: {target_provider}"
            ))
            
            api_key = self.config.get_api_key(target_provider)
            if not api_key:
                state.update_node("validate", ExecutionStatus.ERROR,
                                error_message=f'{target_provider}의 API 키가 설정되지 않음')
                return self._error_response(
                    f'{target_provider}의 API 키가 설정되지 않았습니다.',
                    session_id, state
                )
            
            state.update_node("validate", ExecutionStatus.SUCCESS, {'provider': target_provider})
            
            # ③ API 호출 노드
            state.add_node(WorkflowNode(
                id="api_call",
                type=NodeType.API_CALL,
                name=f"{target_provider} API 호출",
                description="API 요청 전송 중..."
            ))
            state.update_node("api_call", ExecutionStatus.RUNNING)
            
            # 실제 API 호출
            try:
                provider_instance = create_provider(target_provider, api_key)
                provider_instance.initialize()
                result = provider_instance.call(message)
                
                if result['success']:
                    response_text = result['response']
                    state.update_node("api_call", ExecutionStatus.SUCCESS,
                                    {'response': response_text, 'model': target_provider})
                else:
                    error_msg = result['error'] or '알 수 없는 오류'
                    state.update_node("api_call", ExecutionStatus.ERROR,
                                    error_message=error_msg)
                    return self._error_response(error_msg, session_id, state)
                    
            except Exception as e:
                error_msg = f"{target_provider} API 호출 실패: {str(e)}"
                state.update_node("api_call", ExecutionStatus.ERROR, error_message=error_msg)
                return self._error_response(error_msg, session_id, state)
            
            # ④ 응답 처리 노드
            state.add_node(WorkflowNode(
                id="process",
                type=NodeType.PROCESS,
                name="응답 처리",
                description="응답 텍스트 정제"
            ))
            state.update_node("process", ExecutionStatus.SUCCESS,
                            {'processed': True, 'length': len(response_text)})
            
            # ⑤ 출력 노드
            state.add_node(WorkflowNode(
                id="output",
                type=NodeType.OUTPUT,
                name="최종 출력",
                description="사용자에게 응답 반환"
            ))
            state.update_node("output", ExecutionStatus.SUCCESS, {'response': response_text})
            
            state.response = response_text
            
            return {
                'success': True,
                'response': response_text,
                'message': 'API 호출 성공',
                'session_id': session_id,
                'workflow': self._build_workflow_data(session_id)
            }
        
        except Exception as e:
            error_msg = f"워크플로우 실행 오류: {str(e)}"
            state.add_node(WorkflowNode(
                id="error",
                type=NodeType.ERROR,
                name="오류",
                status=ExecutionStatus.ERROR,
                error_message=error_msg
            ))
            return self._error_response(error_msg, session_id, state)

    def call_api(self, message: str, provider: str = None) -> dict:
        """간단한 API 호출 (워크플로우 없음)"""
        target_provider = provider or self.active_provider
        
        if not target_provider:
            return {'success': False, 'response': '',
                   'message': '선택된 AI 제공자가 없습니다.'}

        api_key = self.config.get_api_key(target_provider)
        if not api_key:
            return {'success': False, 'response': '',
                   'message': f'{target_provider}의 API 키가 설정되지 않았습니다.'}

        try:
            provider_instance = create_provider(target_provider, api_key)
            provider_instance.initialize()
            result = provider_instance.call(message)
            
            return {
                'success': result['success'],
                'response': result['response'],
                'message': result['error'] or ''
            }
        except Exception as e:
            return {'success': False, 'response': '',
                   'message': f'API 호출 실패: {str(e)}'}

    # ======================== 워크플로우 관련 ========================
    
    def get_workflow(self, session_id: str) -> dict:
        """워크플로우 데이터 조회"""
        return self.workflow_tracker.generate_workflow_json(session_id)
    
    def get_workflow_html(self, session_id: str) -> str:
        """워크플로우 HTML 조회"""
        return self.workflow_tracker.generate_html_timeline(session_id)

    # ======================== 상태 조회 ========================
    
    def get_status(self) -> dict:
        """현재 상태 조회"""
        return {
            'available_providers': self.list_available_providers(),
            'configured_providers': self.get_configured_providers(),
            'active_provider': self.active_provider,
            'status': self.config.export_keys_summary()
        }

    # ======================== 헬퍼 메서드 ========================
    
    def _error_response(self, message: str, session_id: str, 
                       state: ChatbotState = None) -> Dict[str, Any]:
        """오류 응답 생성"""
        return {
            'success': False,
            'response': '',
            'message': message,
            'session_id': session_id,
            'workflow': self._build_workflow_data(session_id) if state else {}
        }
    
    def _build_workflow_data(self, session_id: str) -> dict:
        """워크플로우 데이터 생성"""
        return {
            'mermaid': self.workflow_tracker.generate_workflow_mermaid(session_id),
            'html': self.workflow_tracker.generate_html_timeline(session_id),
            'json': self.workflow_tracker.generate_workflow_json(session_id)
        }
