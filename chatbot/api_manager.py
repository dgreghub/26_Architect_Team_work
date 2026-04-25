"""
AI API 통합 관리자
- 다양한 AI 제공자 지원
- API 키 관리
- 워크플로우 추적 (LangGraph)
- 동적 프로바이더 로딩
"""
import uuid
from typing import Optional, Dict, Any
from config import ConfigManager
from .models.gemini import DEFAULT_GEMINI_MODEL
from .workflow import WorkflowTracker, ChatbotState, WorkflowNode, NodeType, ExecutionStatus


class APIManager:
    """AI API 통합 관리"""

    def __init__(self):
        self.config = ConfigManager()
        self.active_provider = None
        self.client = None
        self.workflow_tracker = WorkflowTracker()

    def list_available_providers(self) -> list:
        """지원하는 AI 제공자 목록"""
        return self.config.list_available_providers()

    def get_configured_providers(self) -> list:
        """현재 설정된 AI 제공자 목록"""
        return self.config.get_configured_providers()

    def set_api_key(self, provider: str, api_key: str) -> dict:
        """
        API 키 설정 및 검증
        
        Args:
            provider: AI 제공자 ('gemini', 'openai', 'claude', 'custom')
            api_key: API 키
            
        Returns:
            {'success': bool, 'message': str}
        """
        if provider not in self.config.list_available_providers():
            return {
                'success': False,
                'message': f"지원하지 않는 제공자입니다: {provider}"
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
            return {
                'success': False,
                'message': f"오류 발생: {str(e)}"
            }

    def select_provider(self, provider: str) -> dict:
        """
        AI 제공자 선택 및 클라이언트 초기화
        
        Args:
            provider: 선택할 AI 제공자
            
        Returns:
            {'success': bool, 'message': str}
        """
        api_key = self.config.get_api_key(provider)
        
        if not api_key:
            return {
                'success': False,
                'message': f"{provider}의 API 키가 설정되지 않았습니다."
            }

        try:
            self.active_provider = provider
            
            # 실제 클라이언트 초기화
            if provider == 'gemini':
                try:
                    from google import genai
                    self.client = genai.Client(api_key=api_key)
                    return {
                        'success': True,
                        'message': f"✓ {provider} 클라이언트 초기화 성공",
                        'provider': provider
                    }
                except ImportError:
                    return {
                        'success': False,
                        'message': "google-generativeai 패키지가 설치되지 않았습니다. pip install google-generativeai 실행해주세요."
                    }
            elif provider == 'openai':
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=api_key)
                    return {
                        'success': True,
                        'message': f"✓ {provider} 클라이언트 초기화 성공",
                        'provider': provider
                    }
                except ImportError:
                    return {
                        'success': False,
                        'message': "openai 패키지가 설치되지 않았습니다."
                    }
            
            return {
                'success': True,
                'message': f"{provider} 제공자가 선택되었습니다.",
                'provider': provider
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"제공자 선택 실패: {str(e)}"
            }

    def call_api_with_workflow(self, message: str, provider: str = None, session_id: str = None) -> Dict[str, Any]:
        """
        AI API 호출 (워크플로우 추적 포함)
        
        Args:
            message: 사용자 메시지
            provider: AI 제공자 (미지정 시 active_provider 사용)
            session_id: 세션 ID (미지정 시 생성)
            
        Returns:
            {
                'success': bool,
                'response': str,
                'message': str,
                'session_id': str,
                'workflow': dict (시각화 데이터)
            }
        """
        target_provider = provider or self.active_provider
        session_id = session_id or str(uuid.uuid4())
        
        if not target_provider:
            return {
                'success': False,
                'response': '',
                'message': '선택된 AI 제공자가 없습니다.',
                'session_id': session_id
            }

        # 워크플로우 상태 생성
        state = self.workflow_tracker.create_state(session_id, message, target_provider)
        
        try:
            # 1. 입력 노드
            input_node = WorkflowNode(
                id="input",
                type=NodeType.INPUT,
                name="사용자 입력",
                description=f"메시지: {message[:50]}..." if len(message) > 50 else f"메시지: {message}",
                input_data={'message': message}
            )
            state.add_node(input_node)
            state.update_node("input", ExecutionStatus.SUCCESS, {'message': message})
            
            # 2. API 키 검증 노드
            validate_node = WorkflowNode(
                id="validate",
                type=NodeType.PROCESS,
                name="API 키 검증",
                description=f"제공자: {target_provider}"
            )
            state.add_node(validate_node)
            
            api_key = self.config.get_api_key(target_provider)
            if not api_key:
                state.update_node("validate", ExecutionStatus.ERROR, 
                                error_message=f'{target_provider}의 API 키가 설정되지 않았습니다.')
                return self._build_response(False, '', f'{target_provider}의 API 키가 설정되지 않았습니다.', 
                                          session_id, state)
            
            state.update_node("validate", ExecutionStatus.SUCCESS, {'provider': target_provider})
            
            # 3. API 호출 노드
            api_call_node = WorkflowNode(
                id="api_call",
                type=NodeType.API_CALL,
                name=f"{target_provider} API 호출",
                description="생성 모델로 응답 생성 중..."
            )
            state.add_node(api_call_node)
            state.update_node("api_call", ExecutionStatus.RUNNING)
            
            response_text = ""
            
            # 실제 API 호출
            if target_provider == 'gemini':
                try:
                    if not self.client:
                        self.select_provider('gemini')
                    
                    response = self.client.models.generate_content(
                        model=DEFAULT_GEMINI_MODEL,
                        contents=message,
                    )
                    response_text = response.text
                    
                    state.update_node("api_call", ExecutionStatus.SUCCESS, 
                                    {'response': response_text, 'model': DEFAULT_GEMINI_MODEL})
                except Exception as e:
                    error_msg = f"Gemini API 호출 실패: {str(e)}"
                    state.update_node("api_call", ExecutionStatus.ERROR, 
                                    error_message=error_msg)
                    return self._build_response(False, '', error_msg, session_id, state)
            
            elif target_provider == 'openai':
                try:
                    if not self.client:
                        self.select_provider('openai')
                    
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": message}]
                    )
                    response_text = response.choices[0].message.content
                    
                    state.update_node("api_call", ExecutionStatus.SUCCESS, 
                                    {'response': response_text, 'model': 'gpt-3.5-turbo'})
                except Exception as e:
                    error_msg = f"OpenAI API 호출 실패: {str(e)}"
                    state.update_node("api_call", ExecutionStatus.ERROR, 
                                    error_message=error_msg)
                    return self._build_response(False, '', error_msg, session_id, state)
            else:
                error_msg = f"{target_provider} 아직 미지원 제공자입니다."
                state.update_node("api_call", ExecutionStatus.ERROR, 
                                error_message=error_msg)
                return self._build_response(False, '', error_msg, session_id, state)
            
            # 4. 응답 처리 노드
            process_node = WorkflowNode(
                id="process",
                type=NodeType.PROCESS,
                name="응답 처리",
                description="응답 텍스트 정제 및 포맷"
            )
            state.add_node(process_node)
            state.update_node("process", ExecutionStatus.SUCCESS, 
                            {'processed': True, 'length': len(response_text)})
            
            # 5. 출력 노드
            output_node = WorkflowNode(
                id="output",
                type=NodeType.OUTPUT,
                name="최종 출력",
                description="사용자에게 응답 반환"
            )
            state.add_node(output_node)
            state.update_node("output", ExecutionStatus.SUCCESS, 
                            {'response': response_text})
            
            state.response = response_text
            
            return self._build_response(True, response_text, "API 호출 성공", 
                                      session_id, state)
        
        except Exception as e:
            error_msg = f"워크플로우 실행 오류: {str(e)}"
            error_node = WorkflowNode(
                id="error",
                type=NodeType.ERROR,
                name="오류",
                status=ExecutionStatus.ERROR,
                error_message=error_msg
            )
            state.add_node(error_node)
            
            return self._build_response(False, '', error_msg, session_id, state)
    
    def _build_response(self, success: bool, response: str, message: str, 
                       session_id: str, state: ChatbotState) -> dict:
        """응답 빌드"""
        return {
            'success': success,
            'response': response,
            'message': message,
            'session_id': session_id,
            'workflow': {
                'mermaid': self.workflow_tracker.generate_workflow_mermaid(session_id),
                'html': self.workflow_tracker.generate_html_timeline(session_id),
                'json': self.workflow_tracker.generate_workflow_json(session_id)
            }
        }

    def call_api(self, message: str, provider: str = None) -> dict:
        """
        AI API 호출 (간단한 버전)
        
        Args:
            message: 사용자 메시지
            provider: AI 제공자 (미지정 시 active_provider 사용)
            
        Returns:
            {'success': bool, 'response': str, 'message': str}
        """
        target_provider = provider or self.active_provider
        
        if not target_provider:
            return {
                'success': False,
                'response': '',
                'message': '선택된 AI 제공자가 없습니다.'
            }

        api_key = self.config.get_api_key(target_provider)
        if not api_key:
            return {
                'success': False,
                'response': '',
                'message': f'{target_provider}의 API 키가 설정되지 않았습니다.'
            }

        try:
            # Gemini 실제 연동
            if target_provider == 'gemini':
                try:
                    if not self.client:
                        self.select_provider('gemini')
                    
                    response = self.client.models.generate_content(
                        model=DEFAULT_GEMINI_MODEL,
                        contents=message,
                    )
                    return {
                        'success': True,
                        'response': response.text,
                        'message': 'Gemini 응답'
                    }
                except ImportError:
                    return {
                        'success': False,
                        'response': '',
                        'message': 'google-generativeai이 설치되지 않았습니다.'
                    }
            
            # 기본 응답
            return {
                'success': True,
                'response': f"[{target_provider}] 응답 준비 중입니다.",
                'message': ''
            }
        except Exception as e:
            return {
                'success': False,
                'response': '',
                'message': f'API 호출 실패: {str(e)}'
            }

    def get_status(self) -> dict:
        """현재 API 설정 상태 조회"""
        return {
            'available_providers': self.list_available_providers(),
            'configured_providers': self.get_configured_providers(),
            'active_provider': self.active_provider,
            'status': self.config.export_keys_summary()
        }

    def remove_api_key(self, provider: str) -> dict:
        """API 키 삭제"""
        try:
            if self.config.remove_api_key(provider):
                if self.active_provider == provider:
                    self.active_provider = None
                    self.client = None
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
            return {
                'success': False,
                'message': f"오류 발생: {str(e)}"
            }
    
    def get_workflow(self, session_id: str) -> dict:
        """워크플로우 데이터 조회"""
        return self.workflow_tracker.generate_workflow_json(session_id)
    
    def get_workflow_html(self, session_id: str) -> str:
        """워크플로우 HTML 타임라인 조회"""
        return self.workflow_tracker.generate_html_timeline(session_id)
