# 🚀 Gemini API + LangGraph 워크플로우 통합 가이드

## 개요

이 애플리케이션은 **Google Gemini API**를 **LangGraph 기반 워크플로우**로 연동합니다:

- ✅ **Gemini Pro 실시간 연동**: Google Generative AI 직접 호출
- ✅ **LangGraph 워크플로우**: 각 단계별 상태 추적
- ✅ **UI 시각화**: 워크플로우 진행상황을 Gradio에서 실시간 확인
- ✅ **보안 키 관리**: Fernet 암호화 + SOPS 배포 암호화

---

## 🔧 빠른 시작

### 1. Gemini API Key 발급

1. [Google AI Studio](https://aistudio.google.com/app/apikey)에 접속
2. **"Get API Key"** 클릭
3. **"Create API key in new project"** 선택
4. API Key 복사

### 2. 로컬에서 키 설정

```bash
# 앱 실행
python app.py

# 브라우저: http://localhost:7860 접속
```

**Web UI에서:**
1. **🔐 API Settings** 탭 클릭
2. "gemini" 선택
3. API Key 붙여넣기
4. **💾 Save** 클릭

✅ 자동으로 암호화되어 저장됨!

### 3. 채팅 시작

**💬 Chat with Gemini** 탭으로 이동:

1. "🔌 제공자 연결" 클릭
2. 메시지 입력
3. **Send** 클릭

→ Gemini API가 응답합니다!

---

## 📊 LangGraph 워크플로우 구조

### 워크플로우 단계

```
┌─────────────────────────────────────────────────────────────┐
│                    AI 응답 처리 워크플로우                      │
└─────────────────────────────────────────────────────────────┘

① INPUT (입력)
   ↓ 사용자 메시지 수신
   
② VALIDATE (검증)
   ↓ Gemini API 키 확인
   
③ API_CALL (API 호출)
   ↓ Gemini Pro에 요청 전송
   
④ PROCESS (처리)
   ↓ 응답 텍스트 정제
   
⑤ OUTPUT (출력)
   ↓ 사용자에게 응답 반환
```

### 상태별 아이콘

| 상태 | 아이콘 | 설명 |
|------|--------|------|
| SUCCESS | ✓ | 성공 |
| ERROR | ✗ | 실패 |
| RUNNING | ▶ | 진행중 |
| PENDING | ○ | 대기중 |
| SKIPPED | \- | 스킵됨 |

---

## 🎨 UI 탭 설명

### 탭 1: 💬 Chat with Gemini

**메인 채팅 인터페이스**

```
┌─────────────────────────────────────────────┐
│ 좌측: 채팅 히스토리 (600px 높이)             │
│ - 사용자/봇 메시지 표시                      │
│ - 메시지 입력창                              │
│ - Send 버튼                                  │
│                                              │
│ 우측: AI 설정 패널                          │
│ - 제공자 선택 (Gemini/OpenAI/Claude)      │
│ - 제공자 연결 버튼                          │
│ - 연결 상태 표시                            │
└─────────────────────────────────────────────┘
```

**작동 흐름:**
```python
사용자 메시지
    ↓
call_api_with_workflow()  # 워크플로우 생성
    ↓
Gemini API 호출 (5단계 워크플로우)
    ↓
워크플로우 데이터 저장 (session_id)
    ↓
응답을 히스토리에 추가
    ↓
UI 갱신
```

### 탭 2: 🔐 API Settings

**API 키 보안 관리**

- 제공자 선택
- API Key 입력 (비밀번호 필드)
- 저장 시 자동 암호화
- 설정된 제공자 목록 표시

### 탭 3: 📊 Workflow Monitor

**LangGraph 워크플로우 시각화**

```
┌─────────────────────────────────────────┐
│ 진행률 표시:                             │
│ [총 노드] [완료] [오류] [진행중]          │
│                                          │
│ 타임라인:                                │
│ ① ✓ 사용자 입력                         │
│ ② ✓ API 키 검증                        │
│ ③ ▶ Gemini API 호출 (진행중)            │
│ ④ ○ 응답 처리 (대기)                   │
│ ⑤ ○ 최종 출력 (대기)                   │
│                                          │
│ 상세 정보:                               │
│ {                                        │
│   "session_id": "...",                  │
│   "nodes": [...],                       │
│   "summary": {                          │
│     "total_nodes": 5,                   │
│     "completed_nodes": 3,               │
│     "error_nodes": 0                    │
│   }                                      │
│ }                                        │
└─────────────────────────────────────────┘
```

---

## 💻 API 호출 방식

### 워크플로우 포함 호출

```python
from chatbot.api_manager import APIManager

api_manager = APIManager()

# API 키 설정
api_manager.set_api_key('gemini', 'YOUR_GEMINI_API_KEY')

# 워크플로우와 함께 API 호출
result = api_manager.call_api_with_workflow(
    message="안녕하세요, 뭘 도와드릴까요?",
    provider='gemini'
)

# 결과
print(result)
# {
#     'success': True,
#     'response': 'Gemini의 응답...',
#     'session_id': 'uuid...',
#     'workflow': {
#         'mermaid': '...',  # Mermaid 다이어그램
#         'html': '...',     # HTML 타임라인
#         'json': {...}      # JSON 데이터
#     }
# }
```

### 간단한 호출 (워크플로우 없음)

```python
# 간단한 API 호출
result = api_manager.call_api(
    message="메시지",
    provider='gemini'
)

print(result['response'])
```

---

## 📈 워크플로우 데이터 구조

### JSON 형식

```json
{
  "state": {
    "session_id": "abc-123-def",
    "user_message": "안녕하세요",
    "response": "안녕하세요! 무엇을 도와드릴까요?",
    "provider": "gemini",
    "nodes": [
      {
        "id": "input",
        "type": "input",
        "name": "사용자 입력",
        "status": "success",
        "input_data": {"message": "안녕하세요"},
        "timestamp": "2024-04-24T10:30:00.123456"
      },
      {
        "id": "api_call",
        "type": "api_call",
        "name": "Gemini API 호출",
        "status": "success",
        "output_data": {"response": "...", "model": "gemini-pro"},
        "timestamp": "2024-04-24T10:30:00.234567"
      }
      // ... 더 많은 노드
    ],
    "created_at": "2024-04-24T10:30:00.000000",
    "updated_at": "2024-04-24T10:30:00.987654"
  },
  "summary": {
    "total_nodes": 5,
    "completed_nodes": 5,
    "error_nodes": 0,
    "running_nodes": 0,
    "completion_rate": "100%"
  }
}
```

---

## 🔍 오류 처리

### API 키 없음

```
❌ API 키가 설정되지 않았습니다.

해결 방법:
1. API Settings 탭에서 API 키 입력
2. 저장 버튼 클릭
```

### Gemini 패키지 미설치

```
❌ google-generativeai 패키지가 설치되지 않았습니다.

해결 방법:
pip install google-generativeai
```

### API 호출 실패

워크플로우 Monitor 탭에서 오류 발생 위치 확인:

```
① ✓ 사용자 입력
② ✓ API 키 검증  
③ ✗ Gemini API 호출 ← 오류 발생!
   ❌ 429 Too Many Requests
   
해결 방법:
- 요청 빈도 조절
- API 할당량 확인 (Google Cloud Console)
```

---

## 🧪 테스트

```bash
# 전체 테스트
pytest -q

# 워크플로우만 테스트
pytest tests/test_workflow.py -v

# 커버리지 포함
pytest --cov=chatbot --cov=config
```

**테스트 결과:** 28 테스트 통과

---

## 📚 LangGraph와 워크플로우

### LangGraph의 역할

LangGraph는 **상태 기반 워크플로우**를 제공합니다:

```python
# 상태 정의
class ChatbotState:
    session_id: str          # 고유 식별자
    user_message: str        # 사용자 입력
    response: str            # AI 응답
    nodes: List[WorkflowNode] # 실행 단계들
    
# 각 노드는:
- id: 노드 식별자
- type: INPUT, PROCESS, API_CALL, OUTPUT 등
- status: PENDING, RUNNING, SUCCESS, ERROR
- timestamp: 실행 시간 기록
```

### 왜 LangGraph를 사용하는가?

1. **디버깅**: 어디서 실패했는지 정확히 파악
2. **모니터링**: 각 단계의 성능 측정
3. **시각화**: UI에서 워크플로우 확인
4. **확장성**: 복잡한 다단계 프로세스 추가 가능

---

## 🚀 향후 확장 예상

```python
# 1. 다중 제공자 비교
result1 = api_manager.call_api_with_workflow(msg, 'gemini')
result2 = api_manager.call_api_with_workflow(msg, 'openai')

# 2. 조건부 워크플로우
if sentiment == "negative":
    add_node(DECISION, "감정 감지")
    add_node(ESCALATION, "상담원 연결")

# 3. 캐싱
if message in cache:
    use_cached_response()

# 4. 비동기 처리
async def stream_response():
    for token in api_stream(...):
        yield token
```

---

## 📞 트러블슈팅

### Q: 메시지를 보냈는데 응답이 없음

A: 워크플로우 Monitor에서 상태 확인
- ① ✓ 입력 받음
- ② ✓ API 키 검증
- ③ ? API 호출 상태 확인

### Q: "제공자 연결" 버튼을 클릭해도 안됨

A: API Settings에서 API 키를 먼저 저장해야 함

### Q: 같은 메시지를 반복해도 매번 다른 응답

A: Gemini는 항상 다르게 생성하도록 설정됨
- 일관된 응답이 필요하면 `temperature=0` 파라미터 추가

---

## 🔐 보안 체크리스트

- ✅ API 키는 `.secrets.json.enc`에 암호화됨
- ✅ `.secrets.key`는 git에서 무시됨
- ✅ 프로덕션은 SOPS로 추가 암호화
- ✅ 환경변수 우선순위 설정됨
- ✅ 모든 민감 정보는 비밀번호 필드로 입력

---

## 📖 참고 자료

- [Google Generative AI Docs](https://ai.google.dev/)
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)
- [LangChain Docs](https://python.langchain.com/)
- [Gradio Docs](https://www.gradio.app/)

---

## 📊 성능 기준

| 항목 | 값 |
|------|-----|
| Gemini API 응답시간 | ~2-5초 |
| 워크플로우 오버헤드 | <100ms |
| 메모리 사용량 | ~150MB |
| 동시 세션 수 | 제한 없음 (API 할당량만 고려) |

---

**🎉 모두 설정되었습니다! Gemini와 LangGraph로 강력한 AI 챗봇을 구축했습니다!**
