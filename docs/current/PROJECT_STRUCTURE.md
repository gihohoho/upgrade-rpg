# Project Structure — v334

```txt
.
├── AGENTS.md                         # Codex 저장소 규칙
├── NEXT_CHAT_PROMPT.md               # 다음 작업용 prompt
├── NEXT_CHAT_HANDOFF.md              # 현재 handoff
├── README.md                         # 짧은 프로젝트 입구
├── index.html / admin.html / src/    # legacy 게임·관리자
├── .github/workflows/
│   └── publish-backend-ghcr.yml      # 수동 owner-only image publish
├── frontend/vue-app/                 # Vue GET read-only 앱
├── backend/
│   ├── .venv/                        # 로컬 전용, Git 제외
│   ├── app/ / alembic/ / scripts/
│   ├── requirements/                 # exact version + wheel SHA-256 locks
│   ├── Dockerfile                    # 로컬 호환
│   └── Dockerfile.production         # verified production image source
├── deploy/
│   ├── docker-compose.production.yml
│   ├── production.env.example
│   ├── production-deploy-plan.example.json
│   ├── review/                       # sanitized 정적·runtime 증거
│   ├── reverse-proxy/ / secrets/
│   └── isolated-validation/
├── docs/
│   ├── current/                      # 현재 판단과 runbook
│   ├── guides/                       # 실제 사용 가이드
│   ├── contracts/                    # 자동 검사되는 계약
│   ├── handoff/                      # 루트 handoff mirror
│   ├── archive/                      # 고유한 과거 기록
│   └── CHANGELOG.md                  # 단일 현재 변경 이력
└── tools/
    ├── check_*.py / report_*.py      # 정적·읽기 전용 검사
    ├── smoke/                        # backend/frontend/game/contracts smoke
    └── run_smoke_core.sh
```

## 로컬 전용 보존 폴더

`local-backups/`, `local-review-artifacts/`, `backend/.venv/`, `frontend/vue-app/node_modules/`는 Git에서 제외합니다. PostgreSQL backup과 Alembic review 증거가 있으므로 구조 정리 때 자동 삭제하지 않습니다.

legacy `index.html`, `admin.html`, `src/`는 Vue 이식 전까지 경로를 유지합니다. 현재 GHCR repository는 `ghcr.io/gihohoho/upgrade-rpg-backend`입니다.
