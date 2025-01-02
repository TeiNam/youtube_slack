# docker/Dockerfile
FROM python:3.12.8-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 타임존 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# requirements.txt 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY apis/ /app/apis/
COPY utils/ /app/utils/
COPY main.py .

# SQLite 데이터베이스를 위한 볼륨 설정
VOLUME ["/app/data"]

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV DB_PATH=/app/data/youtube_manager.db

# 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]