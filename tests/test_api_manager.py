"""
API 서비스 및 설정 관리 테스트
"""
import pytest
import tempfile
from pathlib import Path
from config import ConfigManager
from config.secrets import SecretsManager
from chatbot.services import APIService


class TestSecretsManager:
    """암호화된 비밀 관리 테스트"""

    def test_save_and_load_secret(self):
        """비밀 저장 및 로드"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SecretsManager(
                secrets_file=str(Path(tmpdir) / ".secrets.json.enc"),
                key_file=str(Path(tmpdir) / ".secrets.key")
            )
            
            test_data = {"api_key_gemini": "test_key_12345"}
            assert manager.save_secret(test_data)
            
            loaded = manager.load_secret()
            assert loaded == test_data

    def test_set_and_get_secret(self):
        """개별 비밀 설정 및 조회"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SecretsManager(
                secrets_file=str(Path(tmpdir) / ".secrets.json.enc"),
                key_file=str(Path(tmpdir) / ".secrets.key")
            )
            
            assert manager.set_secret("test_key", "test_value")
            assert manager.get_secret("test_key") == "test_value"
            assert manager.get_secret("missing_key", "default") == "default"

    def test_delete_secret(self):
        """비밀 삭제"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SecretsManager(
                secrets_file=str(Path(tmpdir) / ".secrets.json.enc"),
                key_file=str(Path(tmpdir) / ".secrets.key")
            )
            
            manager.set_secret("test_key", "test_value")
            assert manager.delete_secret("test_key")
            assert manager.get_secret("test_key") is None

    def test_list_secrets(self):
        """비밀 목록 조회"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = SecretsManager(
                secrets_file=str(Path(tmpdir) / ".secrets.json.enc"),
                key_file=str(Path(tmpdir) / ".secrets.key")
            )
            
            manager.set_secret("key1", "value1")
            manager.set_secret("key2", "value2")
            
            secrets_list = manager.list_secrets()
            assert "key1" in secrets_list
            assert "key2" in secrets_list


class TestConfigManager:
    """설정 관리자 테스트"""

    def test_list_available_providers(self):
        """지원 제공자 목록"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(secrets_dir=tmpdir)
            providers = manager.list_available_providers()
            
            assert 'gemini' in providers
            assert 'openai' in providers
            assert 'claude' in providers

    def test_set_and_get_api_key(self):
        """API 키 설정 및 조회"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(secrets_dir=tmpdir)
            
            assert manager.set_api_key('gemini', 'test_api_key_123')
            key = manager.get_api_key('gemini')
            assert key == 'test_api_key_123'

    def test_get_configured_providers(self):
        """설정된 제공자 목록"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(secrets_dir=tmpdir)
            
            manager.set_api_key('gemini', 'key1')
            manager.set_api_key('openai', 'key2')
            
            configured = manager.get_configured_providers()
            assert 'gemini' in configured
            assert 'openai' in configured

    def test_remove_api_key(self):
        """API 키 삭제"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(secrets_dir=tmpdir)
            
            manager.set_api_key('gemini', 'test_key')
            assert manager.remove_api_key('gemini')
            assert manager.get_api_key('gemini') is None


class TestAPIService:
    """API 서비스 테스트"""

    def test_list_available_providers(self):
        """지원 제공자 목록"""
        api_service = APIService()
        providers = api_service.list_available_providers()
        
        assert isinstance(providers, list)
        assert len(providers) > 0
        assert 'gemini' in providers

    def test_set_api_key_success(self):
        """API 키 설정 성공"""
        api_service = APIService()
        result = api_service.set_api_key('gemini', 'test_key_123')
        
        assert result['success']
        assert 'saved' in result['message'].lower() or 'gemini' in result['message'].lower()

    def test_set_api_key_invalid_provider(self):
        """잘못된 제공자에 API 키 설정"""
        api_service = APIService()
        result = api_service.set_api_key('invalid_provider', 'test_key')
        
        assert not result['success']
        assert 'not supported' in result['message'].lower() or '지원하지 않는' in result['message']

    def test_select_provider_without_key(self):
        """API 키 없이 제공자 선택"""
        api_service = APIService()
        result = api_service.select_provider('openai')
        
        assert not result['success']
        assert 'not set' in result['message'].lower() or '설정되지 않았습니다' in result['message']

    def test_get_status(self):
        """상태 조회"""
        api_service = APIService()
        status = api_service.get_status()
        
        assert 'available_providers' in status
        assert 'configured_providers' in status
        assert 'active_provider' in status
