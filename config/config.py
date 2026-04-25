"""
설정 관리자 - 환경변수, 파일 기반 설정, 암호화된 비밀 통합
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from .secrets import SecretsManager


class ConfigManager:
    """통합 설정 관리자"""

    # 지원하는 AI 제공자
    AI_PROVIDERS = {
        'gemini': 'google.genai',
        'openai': 'openai',
        'claude': 'anthropic',
        'custom': 'custom_api'
    }

    def __init__(self, env_file: str = None, secrets_dir: str = None):
        """
        Args:
            env_file: .env 파일 경로 (기본값: .env)
            secrets_dir: 비밀 저장 디렉토리 (기본값: 프로젝트 루트)
        """
        # 환경변수 로드
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        # 비밀 관리자 초기화
        secrets_dir = Path(secrets_dir or ".")
        self.secrets = SecretsManager(
            secrets_file=str(secrets_dir / ".secrets.json.enc"),
            key_file=str(secrets_dir / ".secrets.key")
        )

    def get_api_key(self, provider: str, from_env: bool = True) -> str:
        """
        AI API 키 조회
        
        우선순위:
        1. 환경변수 (from_env=True일 때)
        2. 암호화된 로컬 저장소
        
        Args:
            provider: AI 제공자 ('gemini', 'openai', 'claude', 'custom')
            from_env: 환경변수에서 먼저 조회할지 여부
            
        Returns:
            API 키 또는 None
        """
        # 환경변수 키 이름
        env_key = f"{provider.upper()}_API_KEY"
        
        # 1. 환경변수 확인
        if from_env:
            api_key = os.getenv(env_key)
            if api_key:
                return api_key
        
        # 2. 암호화된 저장소 확인
        secret_key = f"api_key_{provider}"
        return self.secrets.get_secret(secret_key)

    def set_api_key(self, provider: str, api_key: str) -> bool:
        """
        AI API 키 저장
        
        Args:
            provider: AI 제공자
            api_key: API 키
            
        Returns:
            성공 여부
        """
        secret_key = f"api_key_{provider}"
        return self.secrets.set_secret(secret_key, api_key)

    def get_config_value(self, key: str, default=None):
        """
        설정값 조회 (환경변수 우선)
        
        Args:
            key: 설정 키
            default: 기본값
            
        Returns:
            설정값 또는 기본값
        """
        return os.getenv(key, default)

    def list_available_providers(self) -> list:
        """지원하는 AI 제공자 목록"""
        return list(self.AI_PROVIDERS.keys())

    def get_configured_providers(self) -> list:
        """
        현재 설정된 AI 제공자 목록
        
        Returns:
            API 키가 설정된 제공자 목록
        """
        configured = []
        for provider in self.AI_PROVIDERS.keys():
            if self.get_api_key(provider):
                configured.append(provider)
        return configured

    def remove_api_key(self, provider: str) -> bool:
        """
        API 키 삭제
        
        Args:
            provider: AI 제공자
            
        Returns:
            성공 여부
        """
        secret_key = f"api_key_{provider}"
        return self.secrets.delete_secret(secret_key)

    def export_keys_summary(self) -> dict:
        """설정된 API 키 요약 (값은 마스킹)"""
        summary = {
            "available_providers": self.list_available_providers(),
            "configured_providers": self.get_configured_providers(),
            "secrets_file_exists": self.secrets.secrets_file.exists(),
            "key_file_exists": self.secrets.key_file.exists()
        }
        return summary
