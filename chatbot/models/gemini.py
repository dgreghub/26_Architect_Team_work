"""
Google Gemini AI 제공자
"""
import os
from typing import Dict, Any
from .base import BaseAIProvider


DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")


class GeminiProvider(BaseAIProvider):
    """Google Gemini Pro 제공자"""
    
    def is_available(self) -> bool:
        """google-generativeai 사용 가능 여부"""
        try:
            from google import genai  # noqa: F401
            return True
        except ImportError:
            return False
    
    def initialize(self) -> bool:
        """Gemini 클라이언트 초기화"""
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            return True
        except Exception as e:
            print(f"Gemini 초기화 실패: {e}")
            return False

    def _format_error(self, error: Exception) -> str:
        """Return a user-facing Gemini error message."""
        error_text = str(error)

        if "RESOURCE_EXHAUSTED" in error_text or "429" in error_text:
            return (
                "Gemini API 호출 실패: 사용량 한도(Quota)를 초과했습니다. "
                f"현재 모델은 {DEFAULT_GEMINI_MODEL}입니다. "
                "Google AI Studio의 Rate limit 페이지에서 해당 프로젝트의 RPM/TPM/RPD 한도와 "
                "결제 연결 상태를 확인하세요. 잠시 후 재시도하거나, GEMINI_MODEL 환경변수로 "
                "사용 가능한 다른 모델을 지정할 수 있습니다."
            )

        if "API_KEY_INVALID" in error_text or "INVALID_ARGUMENT" in error_text:
            return "Gemini API 호출 실패: API 키가 유효하지 않습니다. 저장된 Gemini API 키를 다시 확인하세요."

        if "NOT_FOUND" in error_text or "404" in error_text:
            return (
                "Gemini API 호출 실패: 모델을 찾을 수 없거나 generateContent를 지원하지 않습니다. "
                f"현재 모델은 {DEFAULT_GEMINI_MODEL}입니다. "
                "Gemini 3 Flash 기준 모델명은 gemini-3-flash-preview 입니다. "
                "gemini-3-flash-8b는 현재 Gemini API 공식 모델 ID가 아닙니다. "
                "Google AI Studio의 ListModels/Models 페이지에서 이 API 키의 프로젝트가 사용할 수 있는 모델을 확인하세요."
            )

        return f"Gemini API 호출 실패: {error_text}"
    
    def call(self, message: str) -> Dict[str, Any]:
        """Gemini API 호출"""
        if not self.client:
            if not self.initialize():
                return {
                    'success': False,
                    'response': '',
                    'error': 'Gemini 클라이언트 초기화 실패'
                }
        
        try:
            response = self.client.models.generate_content(
                model=DEFAULT_GEMINI_MODEL,
                contents=message,
            )
            return {
                'success': True,
                'response': response.text,
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'response': '',
                'error': self._format_error(e)
            }
