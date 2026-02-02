# 1. 파이썬 베이스 이미지 선택
FROM python:3.10-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. 라이브러리 목록 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. [중요] 무료 모델(HuggingFace) 미리 다운로드 (실행 속도 향상)
RUN python -c "from transformers import pipeline; pipeline('text-classification', model='j-hartmann/emotion-english-distilroberta-base')"

# 6. 소스 코드 복사
COPY . .

# 7. FastAPI 포트 개방
EXPOSE 8000

# 8. 앱 실행 명령
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]