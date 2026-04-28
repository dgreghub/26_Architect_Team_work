# Project Summary

## 개요

이 프로젝트는 Architect Team용 챗봇 PoC입니다. `Gradio` 기반 UI에서 AI 제공자와 대화할 수 있고, `Gemini` 연동과 워크플로우 추적, API 키 보안 저장, Docker/Kubernetes 배포 구성을 포함합니다.

## 핵심 기능

- Gradio UI를 통한 챗봇 사용
- Gemini 중심의 AI 제공자 구조
- LangGraph 스타일 워크플로우 추적 및 시각화
- API 키 로컬 암호화 저장
- Docker 이미지 빌드 및 Kubernetes 배포 준비
- 테스트 코드 포함

## 주요 디렉터리!

```text
26_Architect_Team_work/
|- app.py
|- chatbot/
|  |- core.py
|  |- ui.py
|  |- api_manager.py
|  |- models/
|  |- workflow/
|  `- services/
|- config/
|- tests/
|- k8s/
`- .github/workflows/
```

## 실행 방법

### 로컬 실행

```bash
cp .env.example .env
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

- 기본 접속 주소: `http://localhost:7860`

### Docker

Windows:

```powershell
.\build.ps1 -ImageTag latest
```

Linux/Mac:

```bash
chmod +x build.sh
./build.sh latest
```

## 아키텍처 요약

### `chatbot/`

- `core.py`: 기본 챗봇 응답 로직
- `ui.py`: Gradio 인터페이스
- `api_manager.py`, `services/api_service.py`: 제공자 선택, API 호출, 워크플로우 연계
- `models/`: Gemini/OpenAI/Claude 제공자 추상화
- `workflow/`: 노드, 상태, 추적기 관리

### `config/`

- `config.py`: 설정 관리
- `secrets.py`: API 키 암호화/복호화

### `tests/`

- `test_core.py`: 기본 응답 로직
- `test_api_manager.py`: API/보안 관련 로직
- `test_workflow.py`: 워크플로우 상태/추적 테스트

## 워크플로우 개념

문서 기준 워크플로우는 아래 5단계입니다.

1. 입력 수신
2. API 키 검증
3. AI API 호출
4. 응답 처리
5. 결과 출력

워크플로우 상태는 성공, 실패, 진행중, 대기중 등으로 관리되며, HTML/Mermaid/JSON 형태의 시각화 데이터를 만들 수 있습니다.

## 보안 요약

- 로컬 API 키는 `Fernet` 기반으로 암호화 저장
- 주요 로컬 파일: `.secrets.key`, `.secrets.json.enc`
- Git/배포 환경에서는 `SOPS` 기반 비밀값 관리 방식 사용
- `.env`, `.env.local`, `.secrets.key`, `.secrets.json.enc`는 커밋하면 안 됨

환경변수 우선순위:

1. `.env` / `.env.local`
2. 로컬 암호화 저장소
3. 미설정

## 배포 요약

### Kubernetes

- `k8s/deployment.yaml`
- `k8s/service.yaml`
- `k8s/gateway.yaml`

일반 흐름:

1. Docker 이미지 빌드
2. 레지스트리 푸시
3. Kubernetes 매니페스트 적용
4. 서비스 상태 및 로그 확인

### CI/CD

- `.github/workflows/docker-build-push.yaml` 포함
- 문서에는 GitHub Actions, Jenkins, ArgoCD 기반 흐름이 정리되어 있음
- 현재 저장소 기준으로는 GitHub Actions와 Jenkins 파일이 확인됨

## 테스트

실행 예시:

```bash
pytest -q
```

문서 기준 테스트 범위:

- 핵심 챗봇 로직
- API 제공자/키 관리
- 워크플로우 상태 추적

## 문서별 역할

- `README.md`: 가장 짧은 프로젝트 소개
- `docs/01_README_SETUP.md`: 로컬 실행, Docker, Kubernetes, CI/CD 설정
- `docs/02_ARCHITECTURE.md`: 패키지 구조와 모듈 책임
- `docs/03_SECURITY.md`: API 키 암호화 및 비밀값 관리
- `docs/04_GEMINI_LANGGRAPH.md`: Gemini 연동과 워크플로우 사용 방식

## 빠르게 보면 좋은 순서

1. `SUMMARY.md`
2. `docs/01_README_SETUP.md`
3. `docs/02_ARCHITECTURE.md`
4. `docs/03_SECURITY.md`
5. `docs/04_GEMINI_LANGGRAPH.md`

## 메모

문서들 사이에 일부 표현 차이나 예전 구조 설명이 조금 섞여 있지만, 전체 방향은 일관됩니다. 이 요약 문서는 중복 내용을 줄이고 현재 저장소 기준으로 큰 흐름만 빠르게 파악할 수 있게 정리한 버전입니다.
