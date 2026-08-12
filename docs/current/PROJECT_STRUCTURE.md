# Project Structure — v371

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
│  ├─ app/                      FastAPI routes/services/models/schemas
│  ├─ alembic/                  DB revision source
│  ├─ requirements/             reproducible dependency inputs/locks
│  └─ scripts/                  backend 전용 one-shot/read-only 도구
├─ frontend/vue-app/            Vue read-only 전환 실험
├─ deploy/                      배포 계약·예시·정제된 증거
└─ tools/                       checker·report·smoke·maintenance
```

자동 생성된 backend route/structure/legacy dependency 보고서는 `docs/generated/`에서 확인합니다.

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
