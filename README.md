# 26_Architect_Team_work
26년 아키텍쳐 과제 PoC 진행을 위해 관리 용도로 사용

## 📋 프로젝트 구조

```
26_Architect_Team_work/
├── app.py                          # Gradio 애플리케이션 진입점 (파이프라인)
├── requirements.txt                # Python 의존성
├── Dockerfile                      # Docker 이미지 빌드 설정
├── .dockerignore                   # Docker 빌드 제외 파일
├── .env.example                    # 환경변수 예시
├── jenkinsfile                     # Jenkins CI/CD 파이프라인
├── build.sh                        # Linux/Mac 빌드 스크립트
├── build.ps1                       # Windows 빌드 스크립트
├── chatbot/                        # 챗봇 패키지
│   ├── __init__.py                 # 패키지 초기화
│   ├── core.py                     # 챗봇 로직 (LLM 호출 등)
│   └── ui.py                       # Gradio UI 인터페이스
├── k8s/
│   ├── deployment.yaml             # Kubernetes Deployment (namespace: eshop)
│   └── service.yaml                # Kubernetes Service (namespace: eshop)
├── .github/
│   └── workflows/
│       └── docker-build-push.yaml  # GitHub Actions CI/CD (선택사항)
├── argocd/
│   └── application.yaml            # ArgoCD Application (선택사항)
└── README_SETUP.md                 # 이 파일
```
