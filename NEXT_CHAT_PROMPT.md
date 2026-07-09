이전 채팅에서 이어서 진행한다.
현재 안정 버전은 v226이다.
업로드할 ZIP은 `rpg_v226_backend_admin_runtime_route_contract_ready.zip`이다.

중요한 사용자 선호:
- 사용자는 코딩을 잘 모르는 기호다.
- 설명은 쉽게, 한국어로 한다.
- 터미널 명령은 반드시 “실행 위치: 프로젝트 루트” 또는 “실행 위치: backend 폴더”처럼 위치를 먼저 적고, 그 아래에 복사 가능한 코드 블록으로 준다.
- git add/commit/push는 한 번에 복사할 수 있도록 한 코드 블록으로 묶어서 준다.
- 안전한 작업은 여러 단계 과감하게 묶어도 좋지만, route/schema/API/DB/env 변경처럼 위험한 작업은 천천히 한다.

현재 구조 요약:
- `backend/app/api/routes/admin.py`는 include-router facade다.
- feature route module:
  - `admin_overview_snapshot_routes.py`
  - `admin_master_data_routes.py`
  - `admin_change_log_routes.py`
- route ownership contract:
  - `admin_route_map_contract.py`
- route module import contract:
  - `admin_route_module_import_contract.py`
- runtime route registration contract:
  - `admin_runtime_route_contract.py`
- AdminService facade:
  - `backend/app/services/admin_service.py`
- backend split contract:
  - splitStatus: `admin-runtime-route-contract-v226`

v226에서 한 일:
- FastAPI 앱에 실제 등록된 `/api/v1/admin/...` route 목록을 static route ownership map과 대조하는 contract 추가
- route 누락/예상 밖/중복 method+path 검증 추가
- `/api/v1/admin` prefix 유지 검증 추가
- frontend readiness flag 추가:
  - `backendRuntimeRouteContractReady`
  - `backendRuntimeRouteRegistrationReady`

다음 추천 작업:
- v227 backend admin route operation metadata contract
- route별 endpoint name / operation identity / response type marker를 static/runtime contract로 더 강하게 고정
- route path/schema/API 응답 구조는 바꾸지 말 것
