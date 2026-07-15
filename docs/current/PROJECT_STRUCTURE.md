# Project Structure — v311

## 기준 구조

```txt
.
├── index.html                     # 현재 legacy 게임 진입점
├── admin.html                     # 현재 legacy 관리자 진입점
├── src/                           # legacy JS/CSS, Vue 폴더가 아님
├── frontend/vue-app/              # Vue/Vite read-only 전환 앱
├── backend/                       # FastAPI + SQLAlchemy + Alembic
├── deploy/                        # 운영 배포 정적 template와 계획
├── tools/                         # 검사기·smoke·DB 안전 도구
├── docs/
│   ├── current/                   # 현재 판단과 다음 단계 문서
│   ├── archive/postgres-baseline/ # 완료된 v282~v304 DB 단계 기록
│   ├── archive/runtime-hardening/ # 완료된 일회성 runtime 수정 기록
│   ├── archive/stage-notes/       # 과거 기능 단계 기록
│   ├── contracts/                 # 관리자 contract registry
│   └── handoff/                   # 루트 handoff 문서 동기화 사본
├── NEXT_CHAT_PROMPT.md
└── NEXT_CHAT_HANDOFF.md
```

## 유지 경계

- `index.html`, `admin.html`, 루트 `src/`는 Vue 이식 전까지 이동하지 않습니다.
- `frontend/vue-app/`은 현재 GET read-only API만 연결합니다.
- Preview/Apply/write/인증은 Vue에 연결하지 않습니다.
- backend route path와 response body는 변경하지 않습니다.
- Alembic revision은 `v295_initial_schema` 하나만 유지합니다.
- 실제 DB/env/seed/Docker volume은 승인 없이 변경하지 않습니다.

## backend runtime

```txt
backend/app/core/config.py  # local/production 설정과 fail-closed guard
backend/app/db/session.py   # async engine/session + explicit pool policy
backend/app/main.py         # FastAPI lifespan + engine.dispose()
backend/Dockerfile          # non-root, 자동 Alembic 없음, 현재 worker 1개
```

## deploy 구조

```txt
deploy/
├── docker-compose.production.yml       # 실행 전 별도 승인 필요한 검토 template
├── production.env.example              # 실제 값 없는 변수/TLS 예시
├── production-capacity-plan.example.json # 실제 적용 없는 pool/connection 계산 입력
├── README.md
├── isolated-validation/
│   └── README.md                        # config/build/run/cleanup 승인 단계
└── secrets/
    └── README.md                        # 실제 secret 파일 비포함 규칙
```

실제 `deploy/production.env`, 인증서, password secret은 Git과 전달 ZIP에서 제외합니다.

## v310 정적 검사

```txt
tools/check_production_secrets_tls_container_static.py
tools/smoke/backend/smoke_production_secrets_tls_container_static.py
docs/current/POSTGRES_PRODUCTION_STATIC_VALIDATION.md
```

## v311 계획 검사

```txt
tools/check_production_capacity_tls_network_plan.py
tools/smoke/backend/smoke_production_capacity_tls_network_plan.py
docs/current/POSTGRES_PRODUCTION_CAPACITY_TLS_NETWORK_PLAN.md
deploy/production-capacity-plan.example.json
deploy/isolated-validation/README.md
```

두 검사는 프로젝트 파일만 읽으며 Docker, DB, `.env`, Alembic을 실행하지 않습니다.

## 문서 정리 원칙

- 현재 의사결정과 실행 예정 문서만 `docs/current/`에 둡니다.
- 완료된 baseline·일회성 수정 문서는 삭제하지 않고 `docs/archive/`로 이동합니다.
- 루트와 `docs/handoff/`의 prompt/handoff는 동일해야 합니다.
- 로컬 backup과 실행 증거는 `local-backups/`, `local-review-artifacts/`에만 두고 ZIP/Git에서 제외합니다.
