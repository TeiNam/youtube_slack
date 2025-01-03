# YouTube Slack Notifier

YouTube 채널의 새로운 동영상을 모니터링하고 Slack으로 알림을 보내는 서비스입니다.

## 기능

- YouTube 채널 모니터링
- 새 동영상 업로드 시 Slack 웹훅을 통한 알림
- 다중 채널 및 웹훅 지원
- RESTful API를 통한 채널 및 웹훅 관리

## 시스템 요구사항

- Python 3.12+
- SQLite3
- Docker (선택사항)

## 설치

1. 저장소 클론:
```bash
git clone [repository_url]
cd youtube_slack
```

2. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정:
```bash
# .env 파일 생성
YOUTUBE_API_KEY=your_youtube_api_key
CHECK_INTERVAL=10800 # 3시간
```

## 실행 방법

### 일반 실행
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker를 통한 실행
```bash
cd docker
docker-compose up -d
```

## API 엔드포인트

### 웹훅 관리
- `POST /api/v1/webhooks`: 새 웹훅 등록
- `GET /api/v1/webhooks`: 등록된 웹훅 목록 조회
- `DELETE /api/v1/webhooks/{webhook_id}`: 웹훅 삭제

### 채널 관리
- `POST /api/v1/channels`: 새 YouTube 채널 등록
- `GET /api/v1/channels`: 등록된 채널 목록 조회
- `DELETE /api/v1/channels/{channel_id}`: 채널 삭제

### 서비스 상태 확인
- `GET /status`: 서비스 상태 및 YouTube API 할당량 확인
- `POST /background/start`: 백그라운드 작업 시작
- `POST /background/stop`: 백그라운드 작업 중지

## 프로젝트 구조

```
youtube_slack/
├── apis/                   # API 엔드포인트 구현
│   ├── channel.py         # 채널 관리 API
│   ├── models.py          # Pydantic 모델
│   ├── routers.py         # API 라우터
│   └── webhook.py         # 웹훅 관리 API
├── docker/                # Docker 관련 파일
│   ├── Dockerfile
│   └── docker-compose.yml
├── utils/                 # 유틸리티 모듈
│   ├── config.py         # 설정 관리
│   ├── db_manager.py     # 데이터베이스 관리
│   ├── slack_sender.py   # Slack 알림 전송
│   ├── time_utils.py     # 시간 관련 유틸리티
│   └── youtube_api.py    # YouTube API 클라이언트
├── main.py               # 애플리케이션 메인
└── requirements.txt      # 의존성 패키지 목록
```

## 데이터베이스 스키마

### Webhook 테이블
```sql
CREATE TABLE webhook (
    webhook_id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_name TEXT NOT NULL,        -- 워크스페이스 명
    webhook_name TEXT NOT NULL,          -- 웹훅 명
    url TEXT NOT NULL,                   -- 웹훅 URL
    create_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)
```

### Channel 테이블
```sql
CREATE TABLE channel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    webhook_id INTEGER NOT NULL,         -- 매칭 웹훅ID
    yt_channel_id TEXT NOT NULL,         -- 유튜브 채널 ID
    yt_handling_id TEXT NOT NULL,        -- 핸들링 ID
    yt_ch_name TEXT NOT NULL,            -- 채널명
    last_check_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    create_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (webhook_id) REFERENCES webhook(webhook_id)
)
```

## 주요 기능 설명

1. **채널 모니터링**
   - 등록된 YouTube 채널의 새 동영상을 주기적으로 확인
   - YouTube Data API v3를 사용하여 효율적인 API 할당량 관리
   - 마지막 확인 시간 기준으로 새로운 동영상만 필터링

2. **Slack 알림**
   - 새 동영상 발견 시 설정된 Slack 웹훅으로 알림 전송
   - 알림 내용: 채널명, 동영상 제목, URL, 업로드 시간

3. **백그라운드 작업**
   - 비동기 작업으로 채널 모니터링 수행
   - 설정 가능한 체크 간격 (기본 30분)
   - 시작/중지 API를 통한 모니터링 제어