# 📁 모듈식 패키지 구조 가이드

리팩토링이 완료되었습니다! 이제 코드가 명확한 책임으로 분리되어 이해하기 쉬워졌습니다.

## 🏗️ 새로운 구조

```
chatbot/
├── models/                 # 🤖 AI 제공자 구현
│   ├── base.py            # 추상 기본 클래스
│   ├── gemini.py          # Google Gemini 구현
│   ├── providers.py       # OpenAI, Claude 구현
│   └── __init__.py        # 제공자 레지스트리
│
├── workflow/              # 🔄 LangGraph 상태 관리
│   ├── node.py           # 워크플로우 노드 정의 (NodeType, ExecutionStatus)
│   ├── state.py          # ChatbotState 상태 관리
│   ├── tracker.py        # WorkflowTracker 시각화
│   └── __init__.py       # 모듈 exports
│
├── services/              # 🔧 통합 API 서비스
│   ├── api_service.py    # APIService 오케스트레이션
│   └── __init__.py       # 서비스 exports
│
├── core.py               # 💬 기본 응답 로직
├── ui.py                 # 🎨 Gradio 4-탭 인터페이스
└── __init__.py          # 패키지 exports

config/
├── secrets.py            # 🔐 Fernet 암호화
├── config.py             # ⚙️ 설정 관리
└── __init__.py

tests/
├── test_api_manager.py   # API 서비스 테스트 (13 tests ✅)
├── test_core.py          # 핵심 로직 테스트 (2 tests ✅)
└── test_workflow.py      # 워크플로우 테스트 (13 tests ✅)

app.py                    # 📌 애플리케이션 진입점
```

## 📚 주요 모듈 설명

### 1️⃣ models/ - AI 제공자 추상화

**용도**: 다양한 AI API를 일관된 인터페이스로 제공

```python
from chatbot.models import GeminiProvider, create_provider

# 방법 1: 직접 사용
provider = GeminiProvider(api_key="...")
provider.initialize()
result = provider.call("안녕하세요")

# 방법 2: 레지스트리 사용
provider = create_provider('gemini', api_key="...")
```

**구현된 제공자**:
- ✅ Gemini (Google Generative AI)
- ✅ OpenAI (stub)
- ✅ Claude (stub)

---

### 2️⃣ workflow/ - 상태 추적 및 시각화

**용도**: LangGraph 기반 5-단계 워크플로우 추적

**구성 요소**:

- **node.py**: 
  - `NodeType` enum: INPUT, PROCESS, API_CALL, OUTPUT, DECISION, ERROR
  - `ExecutionStatus` enum: PENDING, RUNNING, SUCCESS, ERROR, SKIPPED
  - `WorkflowNode` dataclass: 개별 노드 정의

- **state.py**:
  - `ChatbotState` dataclass: 전체 워크플로우 상태
  - 노드 추가, 상태 업데이트, 요약 생성

- **tracker.py**:
  - `WorkflowTracker`: 상태 관리 및 시각화
  - Mermaid 다이어그램 생성
  - HTML 타임라인 생성
  - JSON 데이터 export

**사용 예시**:
```python
from chatbot.workflow import WorkflowTracker, ChatbotState, WorkflowNode, NodeType

tracker = WorkflowTracker()
state = tracker.create_state(session_id="123", user_message="안녕")

# 워크플로우 진행 시각화
html = tracker.generate_html_timeline("123")
mermaid = tracker.generate_workflow_mermaid("123")
```

---

### 3️⃣ services/ - 통합 API 서비스

**용도**: API 키 관리 + 제공자 선택 + 워크플로우 추적과 함께 API 호출

**핵심 메서드**:

```python
from chatbot.services import APIService

api_service = APIService()

# 제공자 관리
api_service.list_available_providers()           # ['gemini', 'openai', 'claude']
api_service.set_api_key('gemini', 'sk-...')    # API 키 저장
api_service.select_provider('gemini')            # 제공자 활성화

# API 호출 (워크플로우 자동 추적)
result = api_service.call_api_with_workflow(
    message="안녕하세요",
    provider="gemini"
)
# result = {
#     'success': True,
#     'response': 'AI 응답',
#     'session_id': '...', 
#     'workflow': {mermaid, html, json}
# }

# 워크플로우 조회
html = api_service.get_workflow_html(session_id)
json_data = api_service.get_workflow(session_id)
```

---

### 4️⃣ ui.py - Gradio 인터페이스

**4개 탭**:
1. 💬 **Chat with Gemini** - AI와 채팅
2. 🔐 **API Settings** - API 키 관리
3. 📊 **Workflow Monitor** - LangGraph 진행상황
4. ℹ️ **Info** - 정보

---

## 🔐 보안 계층

```
┌─────────────────────────────────────┐
│  평문 API 키 입력                     │
└────────────┬──────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│  Fernet AES-128 암호화 (로컬)          │
│  → .secrets.json.enc + .secrets.key  │
└────────────┬──────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│  Git 저장 (SOPS 암호화)              │
│  → secrets.enc.yaml + .sops.yaml    │
└─────────────────────────────────────┘
```

---

## 🧪 테스트 (28/28 ✅)

```
tests/test_api_manager.py     13 tests ✅
├── Secrets 암호화             4 tests
├── Config 관리                4 tests
└── APIService 통합            5 tests

tests/test_core.py            2 tests ✅
└── 기본 응답 로직             2 tests

tests/test_workflow.py        13 tests ✅
├── WorkflowNode              2 tests
├── ChatbotState              4 tests
├── WorkflowTracker           5 tests
└── Enums                     2 tests
```

**실행**:
```bash
cd e:\26_Architect_Team_work
.venv\Scripts\python -m pytest tests/ -v
```

---

## 🚀 실행 방법

### 1️⃣ 환경 설정
```bash
# 가상환경 활성화
.venv\Scripts\Activate.ps1

# 의존성 설치 (필요시)
pip install -r requirements.txt
```

### 2️⃣ API 키 설정
```bash
# 환경 변수로 설정
$env:GEMINI_API_KEY = "sk-..."

# 또는 Gradio UI에서 설정
python app.py
# → "🔐 API Settings" 탭에서 입력
```

### 3️⃣ 실행
```bash
python app.py
```

---

## 📊 의존성 관계

```
app.py
  └─ chatbot.ui (UI 표현)
      ├─ chatbot.services.APIService
      │   ├─ chatbot.models (제공자)
      │   ├─ chatbot.workflow (상태 추적)
      │   └─ config (설정 관리)
      └─ chatbot.core (기본 로직)

테스트
  ├─ test_api_manager.py → services, config
  ├─ test_core.py → core
  └─ test_workflow.py → workflow
```

---

## ✨ 장점

### ✅ 가독성 향상
- 각 파일은 **단일 책임**
- 파일당 50-150 줄 (이전 400+ 줄 모놀리식)

### ✅ 유지보수 용이
- AI 제공자 추가: `models/new_provider.py` 추가
- 새 상태 타입: `workflow/node.py` 확장
- 새 기능: `services/api_service.py` 메서드 추가

### ✅ 테스트 용이
- 모듈별 독립 테스트
- Mock 객체 사용 간단

### ✅ 보안
- 3계층 암호화
- 평문 보호

---

## 🔄 리팩토링 전후 비교

| 항목 | 이전 | 이후 |
|------|------|------|
| 파일 수 | 3개 (api_manager, workflow, core) | 12개 (명확한 책임) |
| 평균 파일 크기 | 200-400 줄 | 50-150 줄 |
| 제공자 추가 난이도 | 어려움 (api_manager 수정) | 쉬움 (파일 추가) |
| 테스트 난이도 | 중간 | 쉬움 (모듈별 독립) |
| 새 개발자 학습시간 | 길음 | 짧음 |

---

## 📝 다음 단계

1. ✅ **모듈화** - 완료
2. ⬜ **문서화** - 진행 중 (이 파일)
3. ⬜ **배포** - Docker/K8s 준비
4. ⬜ **CI/CD** - GitHub Actions 자동화

