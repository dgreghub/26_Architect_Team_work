#!/bin/bash

# Docker 이미지 빌드 및 배포 스크립트

set -e

# 환경 변수 설정
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${GCP_REGION:-asia-northeast1}"
IMAGE_NAME="architect-chatbot"
IMAGE_TAG="${1:-latest}"
REGISTRY="gcr.io"

FULL_IMAGE_NAME="${REGISTRY}/${PROJECT_ID}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "=========================================="
echo "Docker 이미지 빌드 시작"
echo "=========================================="
echo "이미지명: ${FULL_IMAGE_NAME}"
echo ""

# Docker 이미지 빌드
echo "[1/3] Docker 이미지 빌드 중..."
docker build -t ${FULL_IMAGE_NAME} -f Dockerfile .

# 로컬에서 테스트 (선택사항)
if [ "${2}" == "--test" ]; then
    echo "[2/3] 로컬 테스트 중... (http://localhost:7860)"
    docker run --rm -p 7860:7860 ${FULL_IMAGE_NAME} &
    sleep 10
    kill %1 2>/dev/null || true
fi

# GCP에 푸시 (선택사항)
if [ "${2}" == "--push" ] || [ "${3}" == "--push" ]; then
    echo "[3/3] GCR에 이미지 푸시 중..."
    docker push ${FULL_IMAGE_NAME}
    echo "✓ 이미지가 성공적으로 푸시되었습니다."
else
    echo "[3/3] 푸시 스킵 (--push 옵션 추가로 GCR에 푸시 가능)"
fi

echo ""
echo "=========================================="
echo "✓ Docker 이미지 빌드 완료!"
echo "=========================================="
echo ""
echo "사용 가능한 명령어:"
echo "  로컬 실행:        docker run -p 7860:7860 ${FULL_IMAGE_NAME}"
echo "  GCR 푸시:        ./build.sh ${IMAGE_TAG} --push"
echo "  빌드 및 테스트:  ./build.sh ${IMAGE_TAG} --test"
echo ""
