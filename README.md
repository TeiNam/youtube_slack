# YouTube Slack Notifier

유튜브 채널의 새로운 동영상을 모니터링하고 Slack으로 알림을 보내는 서비스입니다.

## 주요 기능

- YouTube 채널 등록 및 관리
- 새로운 동영상 자동 감지
- Slack Webhook을 통한 실시간 알림
- 웹 기반 대시보드
- Docker 기반 배포

## 기술 스택

### 백엔드
- Python 3.12
- FastAPI
- YouTube Data API v3
- SQLite
- Slack SDK

### 프론트엔드
- TypeScript
- React
- Vite
- Tailwind CSS

## 시스템 요구사항

- Docker 및 Docker Compose
- YouTube API Key
- Slack Webhook URL

## 설치 및 실행

1. 환경 변수 설정
   ```bash
   # .env 파일 생성
   YOUTUBE_API_KEY=your_youtube_api_key
   ```

2. Docker Compose로 실행
   ```bash
   cd docker
   docker-compose up -d
   ```

   - 백엔드 서버: http://localhost:8000
   - 프론트엔드: http://localhost:5173

## 서비스 구조

```plaintext
.
├── apis/               # FastAPI 라우터 및 API 엔드포인트
├── docker/             # Docker 관련 설정
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── front/             # React 프론트엔드
│   ├── src/
│   └── ...
└── utils/             # 유틸리티 모듈
    ├── config.py
    ├── db_manager.py
    ├── slack_sender.py
    ├── time_utils.py
    └── youtube_api.py
```

## API 엔드포인트

- `POST /api/v1/channels`: YouTube 채널 등록
- `GET /api/v1/channels`: 등록된 채널 목록 조회
- `DELETE /api/v1/channels/{channel_id}`: 채널 삭제
- `POST /api/v1/webhooks`: Slack Webhook 등록
- `GET /api/v1/status`: 서비스 상태 확인

## 주요 업데이트

- 백엔드와 프론트엔드 Docker 컨테이너 분리
- 실시간 상태 모니터링 기능 추가
- YouTube API 쿼터 사용량 추적
- 타임존 설정 최적화 (Asia/Seoul)

## 모니터링 간격

- 기본 체크 간격: 3시간 (환경 변수 CHECK_INTERVAL로 조정 가능)
- 최근 1시간 내 업로드된 영상 감지

## 데이터 저장

- SQLite 데이터베이스 사용
- Docker 볼륨을 통한 데이터 영속성 보장
- 데이터베이스 위치: `docker/data/youtube_manager.db`

## 개발 환경 설정

1. 백엔드 개발 환경
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. 프론트엔드 개발 환경
   ```bash
   cd front
   npm install
   npm run dev
   ```

## 문제 해결

### YouTube API 쿼터 초과
- 일일 쿼터 제한: 10,000 units
- 상태 페이지에서 현재 쿼터 사용량 확인 가능
- 필요한 경우 CHECK_INTERVAL 값을 조정하여 API 호출 빈도 조절

### 시간대 관련 이슈
- 모든 시간은 UTC로 저장되며 표시 시 로컬 시간으로 변환
- Docker 컨테이너의 시간대는 Asia/Seoul로 설정됨

## 라이선스

MIT License