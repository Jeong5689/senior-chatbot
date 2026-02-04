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
# main.py 파일 내의 app 객체를 실행한다는 의미입니다.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]