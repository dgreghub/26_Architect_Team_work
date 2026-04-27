# Architect Team ChatBot - 설정 가이드

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

## 🚀 로컬 실행

### 사전 요구사항

- **Python 3.11 이상** (Docker는 Python 3.11-slim 사용)
- pip, git 설치됨

### 1. 환경 설정

```bash
# 환경변수 파일 생성
cp .env.example .env

# 필요시 .env 파일 수정
# GRADIO_PORT=7860
# GRADIO_HOST=0.0.0.0
```

### 2. Python 3.11 가상환경 생성 및 의존성 설치

```bash
# Python 3.11로 가상환경 생성
py -3.11 -m venv .venv

# 가상환경 활성화
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 3. 로컬에서 실행

```bash
python app.py

# 브라우저에서 http://localhost:7860 접속
```

## 🐳 Docker 이용

### 1. Docker 이미지 빌드

**Windows (PowerShell):**
```powershell
.\build.ps1 -ImageTag latest
```

**Linux/Mac (Bash):**
```bash
chmod +x build.sh
./build.sh latest
```

### 2. 로컬에서 Docker 컨테이너 실행

```bash
docker run -p 7860:7860 gcr.io/YOUR_PROJECT_ID/architect-chatbot:latest
```

### 3. GCR에 이미지 푸시

환경변수 설정:
```bash
export  GCP_PROJECT_ID = 'architect-certification-289902'
export  GCP_REGION = 'us-east1'
```

**Windows (PowerShell):**
```powershell
$env:GCP_PROJECT_ID = "architect-certification-289902"
.\build.ps1 -ImageTag latest -Push
```

**Linux/Mac (Bash):**
```bash
GCP_PROJECT_ID=architect-certification-289902 ./build.sh latest --push
```

## ☸️ Kubernetes 배포

### 1. Deployment 및 Service 배포

```bash
# 이미지 URI 업데이트 (k8s/deployment.yaml에서 PROJECT_ID 변경)
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 상태 확인
kubectl get deployment architect-chatbot
kubectl get service architect-chatbot

# 포드 확인
kubectl get pods -l app=architect-chatbot
```

### 2. 로그 확인

```bash
kubectl logs -l app=architect-chatbot -f
```

### 3. 접속 URL 확인

```bash
kubectl get service architect-chatbot
# LoadBalancer의 EXTERNAL-IP로 접속 가능
```

## 📦 ArgoCD를 이용한 배포

### 1. GitHub Repository 설정

```bash
# GitHub에 현재 repository push
git remote add origin https://github.com/dgreghub/26_Architect_Team_work
git push -u origin main
```

### 2. ArgoCD Application 생성

```bash
# argocd/application.yaml 파일의 repoURL 업데이트
# https://github.com/dgreghub/26_Architect_Team_work 로 변경

# ArgoCD에 적용
kubectl apply -f argocd/application.yaml

# ArgoCD UI에서 확인
argocd app get architect-chatbot
```

### 3. GitHub Actions CI/CD 설정

GitHub Actions를 이용한 자동 배포 설정:

**Secrets 설정 (GitHub Repository Settings > Secrets and variables > Actions):**

1. `GCP_PROJECT_ID`: GCP 프로젝트 ID
2. `WIF_PROVIDER`: Workload Identity Federation Provider
3. `WIF_SERVICE_ACCOUNT`: Workload Identity Service Account

```bash
# GCP에서 서비스 계정 생성 및 설정
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# 필요한 권한 부여
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/container.developer"
```

## 🔄 배포 워크플로우

```
1. GitHub에 코드 Push (main/develop 브랜치)
   ↓
2. GitHub Actions 트리거
   ↓
3. Docker 이미지 빌드 및 GCR에 푸시
   ↓
4. ArgoCD가 변경사항 감지
   ↓
5. Kubernetes에 자동 배포 (Auto-Sync)
   ↓
6. 챗봇 서비스 업데이트 완료
```

## 🔧 주요 설정

### Deployment 리소스

- **Replicas**: 2 (고가용성)
- **Rolling Update**: 무중단 배포
- **Health Check**: Liveness/Readiness Probe 설정
- **보안**: Non-root 사용자, Read-only 파일시스템

### Service

- **Type**: LoadBalancer (외부 접근 가능)
- **Port**: 80 → 7860
- **Session Affinity**: ClientIP (세션 유지)

## 📊 모니터링

### Pod 상태 확인

```bash
kubectl describe pod -l app=architect-chatbot
```

### 메트릭 확인

```bash
kubectl top pod -l app=architect-chatbot
```

### 로그 스트리밍

```bash
kubectl logs -f deployment/architect-chatbot
```

## 🐛 트러블슈팅

### Pod가 시작되지 않음

```bash
# Pod 상태 확인
kubectl describe pod <pod-name>

# 로그 확인
kubectl logs <pod-name>

# 이전 로그 확인
kubectl logs <pod-name> --previous
```

### 이미지를 찾을 수 없음

```bash
# GCR 인증 확인
gcloud auth configure-docker gcr.io

# 이미지 확인
gcloud container images list --project=YOUR_PROJECT_ID
```

### ArgoCD가 동기화하지 않음

```bash
# ArgoCD 로그 확인
kubectl logs -n argocd deployment/argocd-application-controller

# 수동 동기화
argocd app sync architect-chatbot
```

## 📝 다음 단계

1. **LLM 통합**: OpenAI API, Gemini, Llama 등 LLM 연동
2. **데이터베이스**: 대화 이력 저장 (PostgreSQL, Firestore 등)
3. **인증**: 사용자 인증 추가 (OAuth, JWT 등)
4. **모니터링**: Prometheus, Grafana 등 모니터링 시스템 연동
5. **로깅**: Cloud Logging, ELK Stack 등 중앙집중식 로깅

## 📚 참고 자료

- [Gradio 공식 문서](https://www.gradio.app/)
- [Kubernetes 공식 문서](https://kubernetes.io/)
- [ArgoCD 공식 문서](https://argo-cd.readthedocs.io/)
- [Google Cloud Run 배포](https://cloud.google.com/run/docs)
- [GitHub Actions 공식 문서](https://docs.github.com/en/actions)

## 💡 팁

- `build.sh` 또는 `build.ps1` 스크립트로 빌드 과정 자동화
- ArgoCD의 Auto-Sync 기능으로 완전 자동 배포
- GitHub Actions를 이용해 PR 머지 시 자동 배포
- 다양한 환경변수로 개발/스테이징/프로덕션 분리
