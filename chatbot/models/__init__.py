"""
AI 제공자 모델
"""
from .base import BaseAIProvider
from .gemini import GeminiProvider
from .providers import OpenAIProvider, ClaudeProvider

__all__ = [
    'BaseAIProvider',
    'GeminiProvider',
    'OpenAIProvider',
    'ClaudeProvider'
]

# 제공자 레지스트리
PROVIDER_REGISTRY = {
    'gemini': GeminiProvider,
    'openai': OpenAIProvider,
    'claude': ClaudeProvider,
}


def get_provider_class(provider_name: str):
    """제공자 클래스 조회"""
    return PROVIDER_REGISTRY.get(provider_name)


def create_provider(provider_name: str, api_key: str):
    """제공자 인스턴스 생성"""
    provider_class = get_provider_class(provider_name)
    if not provider_class:
        raise ValueError(f"지원하지 않는 제공자: {provider_name}")
    return provider_class(api_key)
