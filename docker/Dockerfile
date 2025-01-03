# docker/Dockerfile
# 프론트엔드 빌드 스테이지
FROM node:18-alpine AS frontend-build
WORKDIR /app/front
COPY front/package*.json ./
RUN npm ci
COPY front/ .
RUN npm run build

# 백엔드 스테이지
FROM python:3.12.8-slim
WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 타임존 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 백엔드 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 정적 파일을 위한 디렉토리 생성
RUN mkdir -p /app/static

# 프론트엔드 빌드 결과물 복사
COPY --from=frontend-build /app/front/dist /app/static

# 백엔드 코드 복사
COPY apis/ /app/apis/
COPY utils/ /app/utils/
COPY main.py .

# SQLite DB를 위한 볼륨
VOLUME ["/app/data"]

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV DB_PATH=/app/data/youtube_manager.db

# 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]