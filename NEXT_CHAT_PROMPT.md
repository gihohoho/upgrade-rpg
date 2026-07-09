바로 직전 채팅에서 이어서 진행합니다.

중요:
- 사용자는 게임 프로젝트의 기획/게임 제작자 이기호이며, 앞으로 기호라고 부릅니다.
- 기호는 코딩/터미널/경로에 익숙하지 않습니다.
- 명령어를 줄 때는 항상 먼저 어디에서 실행해야 하는지 적습니다.
- 주석 기호가 들어간 설명은 코드블록 안에 넣지 말고 코드블록 밖에서 설명합니다.
- 커밋 명령어는 마지막에 add부터 push까지 한 번에 알려줍니다.

현재 안정 버전:
v198: backend admin service split contract

현재 인수인계 ZIP:
rpg_v198_backend_admin_service_split_contract_ready.zip

먼저 확인할 파일:
- NEXT_CHAT_HANDOFF.md
- docs/CURRENT_STATUS.md
- docs/NEXT_STEPS.md
- docs/README.md
- docs/PROJECT_STRUCTURE.md
- docs/BACKEND_ADMIN_SERVICE_SPLIT_CONTRACT.md

v198 완료:
- `backend/app/services/admin_service_split_contract.py` 추가
- `tools/smoke_backend_admin_service_split_contract.py` 추가
- backend admin service 분리 계약 고정
- route/schema 유지 계약 고정
- 브라우저 readiness에 `backendServiceSplitContractReady` 추가

다음 추천 단계:
v199 backend admin overview/snapshots service 실제 분리 1단계.

검증 기준:
- `bash tools/run_smoke_core.sh`
- `bash tools/run_smoke_all.sh`
- `python tools/smoke_backend_admin_service_split_contract.py`
- `python -m compileall -q backend/app`
