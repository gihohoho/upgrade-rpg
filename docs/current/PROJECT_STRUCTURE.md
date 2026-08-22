# Project Structure — v377

## 실행 코드

```text
Upgrade RPG/
├─ index.html, admin.html       legacy 게임·관리자 진입점
├─ src/
│  ├─ api/                      인증, runtime config, backend client
│  ├─ app/                      게임 boot와 상태 연결
│  ├─ assets/                   정적 이미지
│  ├─ data/                     legacy master data
│  ├─ rules/, systems/, ui/     게임 규칙·전투·화면
│  └─ styles/                   legacy CSS
├─ backend/
│  ├─ app/                      FastAPI routes/services/models/schemas/middleware
│  ├─ alembic/                  v371 identity + v377 보안 revision source
│  ├─ requirements/             reproducible dependency inputs/locks
│  └─ scripts/                  backend 전용 one-shot/read-only 도구
├─ frontend/vue-app/            Vue read-only 전환 실험
├─ deploy/                      배포 계약·예시·정제된 증거·v377 release guard
└─ tools/                       checker·report·smoke·migration/release guard·maintenance
```

자동 생성된 backend route/structure/legacy dependency 보고서는 `docs/generated/`에서 확인합니다.

v377은 `backend/app/middleware/`의 JSON 파싱 전 body cap·인증 IP gate,
`backend/app/models/`와 `services/`의 PostgreSQL HMAC rate bucket·semantic email outbox를
추가했습니다. `tools/run_v377_auth_security_migration_roundtrip.py`와
`tools/apply_v377_auth_security_migration.py`는 격리 왕복과 local/Neon의 새 backup 기반
exact apply를 분리합니다. `tools/private_artifacts.py`는 dotenv·DB backup·migration evidence의
Windows exact DACL/POSIX owner-mode 검증과 내용 기록 전 private atomic create를 공통으로
담당하고, `tools/postgres_client_safety.py`는 inherited libpq 환경 제거와 POSIX client 실행파일
trust 경계를 담당합니다. `deploy/v377-email-release-guard.example.json`,
`tools/prepare_v377_email_release.py`, `tools/smoke/backend/smoke_v377_email_release.py`는
미래의 GitHub Actions/GHCR/기존 Render service 단일 배포에 필요한 source-only guard와
회귀 검사를 정의합니다. private environment 준비는 완료됐지만 `8db9bcb`의 격리 왕복과
local backup은 canonicalization 수정 뒤 SHA-stale이며, local apply는 Alembic 전에 안전
중단되어 marker만 보존합니다. 다음 구조 변경은 기존 marker를 지우지 않는 새
recovery namespace·artifact·confirmation 계약이며 실제 local/Neon DB·provider·배포 완료를
뜻하지 않습니다.

## 문서

```text
docs/
├─ README.md                    전체 문서 허브
├─ DOCUMENTATION_SYSTEM.md      위치·중복·Obsidian 운영 규칙
├─ current/                     현재 판단·승인 문서
├─ reference/
│  ├─ database/                 PostgreSQL·Alembic·Neon
│  ├─ backend/                  backend 구조·runtime 감사
│  ├─ frontend/                 Vue·CORS·read-only API
│  └─ assets/                   장비 공식·이미지 규칙
├─ generated/                   도구가 재생성하는 보고서
├─ contracts/                   API·관리자 계약
├─ guides/                      사람이 따라 하는 실행 절차
└─ archive/history/             완료 단계 통합 역사
```

새 채팅은 루트 `AGENTS.md` → `NEXT_CHAT_HANDOFF.md` → `docs/current/CURRENT_STATUS.md`만 먼저 읽습니다. 문서 이동·추가는 `docs/DOCUMENTATION_SYSTEM.md`를 따릅니다.
