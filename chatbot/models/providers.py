"""
OpenAI, Claude 등 기타 AI 제공자
"""
from typing import Dict, Any
from .base import BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    """OpenAI 제공자"""
    
    def is_available(self) -> bool:
        """openai 패키지 사용 가능 여부"""
        try:
            import openai
            return True
        except ImportError:
            return False
    
    def initialize(self) -> bool:
        """OpenAI 클라이언트 초기화"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            return True
        except Exception as e:
            print(f"OpenAI 초기화 실패: {e}")
            return False
    
    def call(self, message: str) -> Dict[str, Any]:
        """OpenAI API 호출"""
        if not self.client:
            if not self.initialize():
                return {
                    'success': False,
                    'response': '',
                    'error': 'OpenAI 클라이언트 초기화 실패'
                }
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}]
            )
            return {
                'success': True,
                'response': response.choices[0].message.content,
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'response': '',
                'error': f'OpenAI API 호출 실패: {str(e)}'
            }


class ClaudeProvider(BaseAIProvider):
    """Claude (Anthropic) 제공자"""
    
    def is_available(self) -> bool:
        """anthropic 패키지 사용 가능 여부"""
        try:
            import anthropic
            return True
        except ImportError:
            return False
    
    def initialize(self) -> bool:
        """Claude 클라이언트 초기화"""
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
            return True
        except Exception as e:
            print(f"Claude 초기화 실패: {e}")
            return False
    
    def call(self, message: str) -> Dict[str, Any]:
        """Claude API 호출"""
        if not self.client:
            if not self.initialize():
                return {
                    'success': False,
                    'response': '',
                    'error': 'Claude 클라이언트 초기화 실패'
                }
        
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                messages=[{"role": "user", "content": message}]
            )
            return {
                'success': True,
                'response': response.content[0].text,
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'response': '',
                'error': f'Claude API 호출 실패: {str(e)}'
            }
