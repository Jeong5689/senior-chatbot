# 1. 파이썬 환경 설정
FROM python:3.10-slim
WORKDIR /app

# 2. 필수 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. 라이브러리 설치 (requirements.txt가 바뀔 때만 실행됨)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. AI 모델 미리 다운로드 (모델 설정이 바뀔 때만 실행됨)
RUN python -c "from transformers import pipeline; pipeline('text-classification', model='j-hartmann/emotion-english-distilroberta-base')"

# 5. 소스 코드 복사 (가장 마지막에 배치하여 빌드 속도 최적화)
COPY . .

# 6. 실행 명령어
# Render는 내부적으로 가변 포트를 사용하므로 $PORT 환경변수를 인식해야 합니다.
# 쉘(sh)을 실행하여 환경변수를 주입하는 방식으로 변경합니다.
#CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
# 6. 실행 명령어 (Render의 가변 포트를 강제로 바인딩)
# $PORT 변수가 있으면 그 값을 쓰고, 없으면 8000을 쓰도록 설정합니다.
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}