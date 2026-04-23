# Multi-stage build for smaller image size
FROM python:3.11-slim as builder

WORKDIR /app

# 시스템 패키지 업데이트 및 필수 라이브러리 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# 최종 이미지
FROM python:3.11-slim

WORKDIR /app

# 보안 및 성능 개선
RUN useradd -m -u 1000 appuser && \
    apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# builder에서 설치된 패키지 복사
COPY --from=builder /root/.local /home/appuser/.local

# 환경 변수 설정
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    GRADIO_HOST=0.0.0.0 \
    GRADIO_PORT=7860

# 애플리케이션 코드 복사
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser chatbot ./chatbot

# 사용자 변경
USER appuser

# 포트 노출
EXPOSE 7860

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860').read()" || exit 1

# 애플리케이션 실행
CMD ["python", "app.py"]
