# 🔐 보안 API Key 관리 가이드

## 개요

이 애플리케이션은 **엔터프라이즈급 보안**을 갖춘 API Key 관리 시스템을 제공합니다:

- ✅ **로컬 암호화**: Fernet (AES-128) 기반 암호화
- ✅ **Git 보안**: SOPS를 사용한 파일 레벨 암호화
- ✅ **사용자 친화적**: Web UI에서 직접 키 관리 가능
- ✅ **AI 의존성 없음**: 암호화된 저장소에서 자동 로드

---

## 🚀 빠른 시작

### 1. 로컬 개발 환경 설정

```bash
# 가상환경 활성화
.\.venv\Scripts\Activate.ps1

# 의존성 설치
pip install -r requirements.txt

# 앱 실행
python app.py
```

브라우저: `http://localhost:7860`

### 2. API Key 설정

UI의 **🔐 API Settings** 탭에서:

1. **AI 제공자** 선택 (Gemini, OpenAI, Claude 등)
2. **API Key** 입력
3. **💾 Save** 버튼 클릭

✅ 자동으로 암호화되어 로컬에 저장됩니다!

---

## 🏗️ 아키텍처

### 로컬 암호화 (개발 환경)

```
┌─────────────────┐
│  사용자 입력    │
│  API Key        │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   config/secrets.py                 │
│   ┌─────────────────────────────┐   │
│   │ SecretsManager              │   │
│   │ - Fernet 암호화             │   │
│   │ - JSON 저장                 │   │
│   └─────────────────────────────┘   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│ .secrets.key    │     │.secrets.json │
│ (암호화 키)     │     │.enc (암호된) │
│ ❌ gitignored   │     │ ❌ gitignored│
└─────────────────┘     └──────────────┘
```

### 프로덕션 암호화 (Git)

```
┌─────────────────────────────────────┐
│        secrets.yaml                 │
│   (평문 - 로컬에서만 사용)           │
└────────┬────────────────────────────┘
         │
         ▼  SOPS 암호화
         │  (git pre-commit)
         ▼
┌──────────────────────────────────────┐
│   secrets.enc.yaml                   │
│   (SOPS 암호화됨)                     │
│   ✅ Git에 커밋됨                     │
│   ✅ CI/CD에서 자동 복호화             │
└──────────────────────────────────────┘
```

---

## 📁 파일 구조

```
26_Architect_Team_work/
├── config/
│   ├── __init__.py
│   ├── secrets.py          # 암호화/복호화 핵심
│   └── config.py           # 설정 관리자
│
├── chatbot/
│   ├── core.py             # 챗봇 로직
│   ├── ui.py               # Gradio UI (API Settings 포함)
│   └── api_manager.py      # API 키/제공자 관리
│
├── tests/
│   ├── test_core.py        # 챗봇 로직 테스트
│   └── test_api_manager.py # 보안 기능 테스트
│
├── .env                    # 환경변수 (git 무시)
├── .env.local              # 로컬만 사용 (git 무시)
├── .secrets.key            # 암호화 키 (git 무시)
├── .secrets.json.enc       # 암호화된 키 저장소 (git 무시)
│
├── .sops.yaml              # SOPS 설정 (git 포함)
├── secrets.yaml.example    # 템플릿 (git 포함)
└── .gitignore              # 보안 파일 제외
```

---

## 🔐 지원하는 AI 제공자

| 제공자 | 환경변수 | 설정 방법 |
|--------|---------|---------|
| **Gemini** | `GEMINI_API_KEY` | UI 또는 .env |
| **OpenAI** | `OPENAI_API_KEY` | UI 또는 .env |
| **Claude** | `CLAUDE_API_KEY` | UI 또는 .env |
| **Custom** | `CUSTOM_API_KEY` | UI 또는 .env |

### 환경변수 우선순위

```python
1. 환경변수 (.env / .env.local) ← 가장 높음
2. 로컬 암호화 저장소 (.secrets.json.enc)
3. None (미설정)
```

---

## 🛡️ 보안 기능 상세

### 1. Fernet 암호화 (로컬)

**알고리즘**: AES-128 CBC + HMAC

```python
# 자동 암호화/복호화
secrets = SecretsManager()
secrets.set_secret('api_key_gemini', 'your_key_here')
key = secrets.get_secret('api_key_gemini')
```

**특징**:
- 타임스탬프 포함 (재생 공격 방지)
- HMAC 무결성 검증
- 자동 키 생성 및 관리

### 2. SOPS 암호화 (Git)

**지원 백엔드**:
- 🔑 AGE (로컬 키 기반)
- ☁️ AWS KMS (클라우드)
- ☁️ GCP Cloud KMS (Google Cloud)
- ☁️ Azure Key Vault

**설정 예시**:

```yaml
# .sops.yaml
creation_rules:
  - path_regex: secrets.*\.enc\.yaml
    key_groups:
    - age:
        - AGE-PUBLIC-KEY-xxxxx
    type: yaml
```

---

## 📝 사용 예시

### 1. 프로그래밍 방식

```python
from config import ConfigManager

config = ConfigManager()

# API Key 설정
config.set_api_key('gemini', 'your_api_key_here')

# API Key 조회
key = config.get_api_key('gemini')

# 설정된 제공자 목록
providers = config.get_configured_providers()
```

### 2. Web UI 방식

1. `http://localhost:7860` 접속
2. **🔐 API Settings** 탭 클릭
3. AI 제공자 선택
4. API Key 입력
5. **💾 Save** 클릭

---

## 🚢 배포 및 CI/CD

### GitHub Actions 예시

```yaml
name: Deploy with SOPS

on: [push]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Decrypt secrets with SOPS
        env:
          SOPS_AGE_KEY: ${{ secrets.SOPS_AGE_KEY }}
        run: |
          sops -d secrets.enc.yaml > secrets.yaml
      
      - name: Build and Deploy
        run: |
          docker build -t app .
          docker run --env-file secrets.yaml app
```

### 환경변수 설정 (CI/CD)

```bash
# GitHub Secrets에 설정
SOPS_AGE_KEY=AGE-SECRET-KEY-xxxxx

# GitLab CI Variables에 설정
SOPS_AGE_KEY_FILE=/tmp/age_key.txt
```

---

## ⚠️ 주의사항

### ❌ 하면 안 되는 것

```bash
# ❌ Git에 커밋하면 안됨
.secrets.key           # 암호화 키
.secrets.json.enc      # 로컬 저장소 (공개되지 않지만)
.env                   # 환경변수
.env.local             # 로컬 환경변수
```

### ✅ 해야 하는 것

```bash
# ✅ .gitignore에 이미 추가됨
# .gitignore 확인
cat .gitignore | grep secrets

# ✅ Git에 커밋 가능
.sops.yaml             # SOPS 설정
secrets.yaml.example   # 템플릿
requirements.txt       # 의존성
```

---

## 🧪 테스트

```bash
# 모든 테스트 실행
pytest -q

# 보안 기능만 테스트
pytest tests/test_api_manager.py -v

# 커버리지 확인
pytest --cov=config --cov=chatbot
```

---

## 🐛 문제 해결

### Q: API Key를 저장했는데 다시 로드되지 않음

```python
# 원인: 암호화 키가 변경되었을 가능성
# 해결:
# 1. .secrets.key 파일 확인
# 2. .secrets.json.enc 재생성
rm .secrets.key .secrets.json.enc
```

### Q: SOPS로 파일을 암호화하려는데 실패

```bash
# AGE 키 확인
export SOPS_AGE_KEY_FILE=~/.sops/key.txt
sops -e secrets.yaml

# AGE 키 생성 (처음일 때)
age-keygen -o ~/.sops/key.txt
```

---

## 📚 참고 자료

- [Cryptography 문서](https://cryptography.io/)
- [SOPS GitHub](https://github.com/mozilla/sops)
- [AGE 암호화](https://github.com/FiloSottile/age)
- [Gradio 문서](https://www.gradio.app/)

---

## 📞 지원

문제가 있으면 다음을 확인하세요:

1. `.gitignore` - 민감한 파일이 git에 커밋되지 않았는지
2. `requirements.txt` - 모든 의존성 설치 확인
3. `pytest` - 테스트 통과 확인
4. 로그 - `app.py` 실행 시 에러 메시지 확인
