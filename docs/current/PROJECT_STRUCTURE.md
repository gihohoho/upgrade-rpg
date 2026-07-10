# Project Structure — v234

현재 ZIP 기준 주요 구조입니다.

```txt
.
├── index.html
├── admin.html
├── README.md
├── README_BACKEND_READY.md
├── NEXT_CHAT_HANDOFF.md
├── NEXT_CHAT_PROMPT.md
├── docker-compose.yml
├── backend/
├── docs/
├── src/
└── tools/
```

## 루트 파일

- `index.html` — 현재 실제 게임 화면. 아직 Vue가 아니라 기존 HTML/JS/CSS 기반입니다.
- `admin.html` — 관리자 페이지입니다.
- `README.md` — 현재 안정 버전 요약입니다.
- `README_BACKEND_READY.md` — 백엔드 readiness 요약입니다.
- `NEXT_CHAT_HANDOFF.md` — 새 채팅 인수인계 핵심 문서입니다.
- `NEXT_CHAT_PROMPT.md` — 새 채팅에 그대로 붙여넣기 좋은 프롬프트입니다.
- `docker-compose.yml` — PostgreSQL / Adminer 로컬 실행 설정입니다.

## backend

FastAPI 백엔드입니다.

주요 역할:

- master-data API
- save snapshot API
- admin read/write API
- create / delete / restore / rollback 제한 API
- PostgreSQL 연동

중요 파일:

```txt
backend/app/main.py
backend/app/api/routes/admin.py
backend/app/api/routes/admin_overview_snapshot_routes.py
backend/app/api/routes/admin_master_data_routes.py
backend/app/api/routes/admin_change_log_routes.py
backend/app/api/routes/admin_request_metadata_contract.py
backend/app/services/admin_service.py
backend/app/services/admin_service_split_contract.py
backend/app/schemas/admin.py
```

## backend/app/api/routes

관리자 route는 기능별 파일로 분리되어 있습니다.

- `admin.py` — include-router facade
- `admin_overview_snapshot_routes.py` — requirements / overview / save-snapshots / change-preview
- `admin_master_data_routes.py` — master-data catalog/detail/create/edit/relation
- `admin_change_log_routes.py` — change-logs / rollback / create-delete / restore

관리자 route contract 파일:

- `admin_route_map_contract.py`
- `admin_route_module_import_contract.py`
- `admin_runtime_route_contract.py`
- `admin_route_operation_contract.py`
- `admin_openapi_route_contract.py`
- `admin_response_metadata_contract.py`
- `admin_request_metadata_contract.py`

## backend/app/services

`AdminService`는 facade이고, 실제 기능은 mixin service로 분리되어 있습니다.

- `admin_service.py` — facade
- `admin_service_split_contract.py` — backend split readiness contract
- `admin/admin_config.py`
- `admin/admin_shared_utils.py`
- `admin/admin_readiness_service.py`
- `admin/admin_overview_snapshots_service.py`
- `admin/admin_master_catalog_service.py`
- `admin/admin_create_lifecycle_service.py`
- `admin/admin_change_log_service.py`
- `admin/admin_edit_draft_service.py`

## src

브라우저에서 사용하는 JS 모듈입니다.

주요 역할:

- master-data fetch / fallback
- save-data bridge
- admin page helper
- 분리된 관리자 layout / field help / settings helpers / change logs / create lifecycle / edit draft / master catalog / overview snapshots helper
- smoke에서 확인하는 브라우저 helper 함수 제공

중요 파일:

```txt
src/api/admin-page-readonly.js
src/api/admin/admin-change-logs.js
src/api/admin/admin-create-lifecycle.js
src/api/admin/admin-edit-draft.js
src/api/admin/admin-master-catalog.js
src/api/admin/admin-overview-snapshots.js
```

## docs

새 채팅에서 우선 볼 문서:

- `docs/CURRENT_STATUS.md`
- `docs/NEXT_STEPS.md`
- `docs/README.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/CHANGELOG.md`

과거 단계 문서:

- `docs/archive/stage-notes/`

## tools

smoke test와 점검 스크립트 폴더입니다.

자주 쓰는 명령:

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_all.sh
```

## ZIP 포함/제외 원칙

포함:

- 전체 프로젝트 소스
- `backend/`
- `src/`
- `docs/`
- `tools/`
- `.env.example`

제외:

- `.env`
- `.git`
- `.venv`
- `node_modules`
- `__pycache__`
- `.pyc`
- 임시 로그/캐시
- 이전 채팅 작업용 `/mnt/data/rpg_v*_work` 폴더
