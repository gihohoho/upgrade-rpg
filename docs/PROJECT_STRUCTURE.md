# Project Structure

현재 ZIP 기준 주요 구조입니다.

```txt
.
├── index.html
├── admin.html
├── README.md
├── NEXT_CHAT_HANDOFF.md
├── NEXT_CHAT_PROMPT.md
├── docker-compose.yml
├── backend/
├── data/
├── docs/
├── src/
└── tools/
```

## 루트 파일

- `index.html` — 현재 실제 게임 화면. 아직 Vue가 아니라 기존 HTML/JS/CSS 기반입니다.
- `admin.html` — 관리자 페이지. 현재 기능이 많아져 sidebar / sticky header / 접기·펼치기 shell이 적용되어 있습니다.
- `README.md` — 현재 안정 버전 요약.
- `NEXT_CHAT_HANDOFF.md` — 새 채팅 인수인계용 핵심 문서.
- `NEXT_CHAT_PROMPT.md` — 새 채팅에 붙여넣기 좋은 프롬프트.
- `docker-compose.yml` — PostgreSQL / Adminer 로컬 실행 설정.

## backend

FastAPI 백엔드입니다.

주요 역할:

- master-data API
- save snapshot API
- admin read/write API
- create / delete / restore 제한 API
- PostgreSQL 연동

중요 파일 예시:

- `backend/app/main.py`
- `backend/app/api/routes/admin.py`
- `backend/app/services/admin_service.py`
- `backend/app/schemas/admin.py`

## src

브라우저에서 사용하는 JS 모듈입니다.

주요 역할:

- master-data fetch / fallback
- save-data bridge
- admin page helper / 분리된 관리자 layout·change logs·create lifecycle·edit draft·master catalog/detail·overview/snapshots helper / bootstrap thin entry
- smoke에서 확인하는 브라우저 helper 함수 제공

중요 파일 예시:

- `src/api/game-api-client.js`
- `src/api/admin-layout-shell.js`
- `src/api/admin/admin-change-logs.js`
- `src/api/admin/admin-create-lifecycle.js`
- `src/api/admin/admin-edit-draft.js`
- `src/api/admin/admin-master-catalog.js`
- `src/api/admin/admin-overview-snapshots.js`
- `src/api/admin-page-readonly.js` — v194 기준 bootstrap/bindEvents/window wrapper 중심 thin entry

## docs

문서 폴더입니다.

새 채팅에서 우선 볼 문서:

- `docs/CURRENT_STATUS.md`
- `docs/NEXT_STEPS.md`
- `docs/README.md`
- `docs/PROJECT_STRUCTURE.md`

과거 단계 문서:

- `docs/archive/stage-notes/`

## tools

smoke test와 점검 스크립트 폴더입니다.

가장 자주 쓰는 명령:

```bash
위치: 프로젝트 루트
bash tools/run_smoke_core.sh
```

```bash
위치: 프로젝트 루트
bash tools/run_smoke_all.sh
```

## ZIP 포함/제외 원칙

포함:

- 전체 프로젝트 소스
- backend / src / docs / tools
- `.env.example`

제외:

- `.env`
- `.gitignore` 변경 없을 때
- `.git`
- `.venv`
- `node_modules`
- `__pycache__`
- `.pyc`
- 임시 로그/캐시
