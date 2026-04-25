"""
AI 제공자 추상 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAIProvider(ABC):
    """AI 제공자 추상 클래스"""
    
    def __init__(self, api_key: str):
        """
        Args:
            api_key: API 키
        """
        self.api_key = api_key
        self.client = None
    
    @abstractmethod
    def initialize(self) -> bool:
        """클라이언트 초기화"""
        pass
    
    @abstractmethod
    def call(self, message: str) -> Dict[str, Any]:
        """
        API 호출
        
        Returns:
            {'success': bool, 'response': str, 'error': str}
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """라이브러리 사용 가능 여부"""
        pass
