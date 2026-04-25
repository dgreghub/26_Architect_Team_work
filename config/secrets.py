"""
암호화/복호화를 통한 보안 키 관리
- 로컬: cryptography 라이브러리 기반 Fernet 암호화
- 로드/저장: JSON 형식
"""
import os
import json
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken


class SecretsManager:
    """API 키 및 민감한 정보 암호화 관리"""

    def __init__(self, secrets_file: str = None, key_file: str = None):
        """
        Args:
            secrets_file: 암호화된 비밀 저장 파일 경로
            key_file: 암호화 키 파일 경로 (절대 git에 커밋하면 안됨)
        """
        self.secrets_file = Path(secrets_file or ".secrets.json.enc")
        self.key_file = Path(key_file or ".secrets.key")
        self._cipher = None

    def _get_or_create_key(self) -> Fernet:
        """암호화 키 로드 또는 생성"""
        if self._cipher:
            return self._cipher

        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            # 새 키 생성
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # .gitignore에 추가되어있는지 확인 (수동 확인 필요)

        self._cipher = Fernet(key)
        return self._cipher

    def save_secret(self, secret_dict: dict) -> bool:
        """
        비밀 정보를 암호화하여 저장
        
        Args:
            secret_dict: 저장할 비밀 정보 (dict)
            
        Returns:
            성공 여부
        """
        try:
            cipher = self._get_or_create_key()
            json_str = json.dumps(secret_dict, ensure_ascii=False)
            encrypted = cipher.encrypt(json_str.encode('utf-8'))
            
            with open(self.secrets_file, 'wb') as f:
                f.write(encrypted)
            return True
        except Exception as e:
            print(f"[ERROR] 비밀 저장 실패: {e}")
            return False

    def load_secret(self) -> dict:
        """
        암호화된 비밀 정보 복호화하여 로드
        
        Returns:
            복호화된 비밀 정보 (dict), 실패 시 {}
        """
        try:
            if not self.secrets_file.exists():
                return {}

            cipher = self._get_or_create_key()
            with open(self.secrets_file, 'rb') as f:
                encrypted = f.read()

            decrypted = cipher.decrypt(encrypted)
            return json.loads(decrypted.decode('utf-8'))
        except InvalidToken:
            print("[ERROR] 암호화 키가 맞지 않습니다. 비밀 파일을 다시 생성해주세요.")
            return {}
        except Exception as e:
            print(f"[ERROR] 비밀 로드 실패: {e}")
            return {}

    def get_secret(self, key: str, default=None):
        """
        특정 비밀 정보 조회
        
        Args:
            key: 비밀 키 이름
            default: 기본값
            
        Returns:
            비밀 값 또는 기본값
        """
        secrets = self.load_secret()
        return secrets.get(key, default)

    def set_secret(self, key: str, value: str) -> bool:
        """
        특정 비밀 정보 설정 및 저장
        
        Args:
            key: 비밀 키 이름
            value: 비밀 값
            
        Returns:
            성공 여부
        """
        secrets = self.load_secret()
        secrets[key] = value
        return self.save_secret(secrets)

    def delete_secret(self, key: str) -> bool:
        """
        특정 비밀 정보 삭제
        
        Args:
            key: 삭제할 비밀 키 이름
            
        Returns:
            성공 여부
        """
        secrets = self.load_secret()
        if key in secrets:
            del secrets[key]
            return self.save_secret(secrets)
        return False

    def list_secrets(self) -> list:
        """
        저장된 모든 비밀 키 목록 (값은 마스킹)
        
        Returns:
            비밀 키 목록 (값은 표시 안함)
        """
        secrets = self.load_secret()
        return list(secrets.keys())
