이전 채팅에서 이어서 진행합니다.

현재 안정 버전은 v220입니다.
업로드할 ZIP은 `rpg_v220_backend_admin_route_service_legacy_cleanup_ready.zip`입니다.

작업 조건:
- API route path 변경 금지
- schema 변경 금지
- API 응답 구조 변경 금지
- DB/env 변경 금지
- 기능이 잘 되는 상태를 우선 유지
- 위험 낮은 정리는 여러 단계 묶어도 됨
- 안정성이 필요한 작업은 천천히 smoke를 추가하며 진행
- 터미널 명령은 반드시 어느 폴더에서 실행하는지 먼저 알려주고, 복사 가능한 코드 블록으로 제공
- git add/commit/push는 한 번에 복사 가능한 한 코드 블록으로 제공

현재 상태:
- `admin.py`는 router include facade로만 유지됨
- master-data routes: `admin_master_data_routes.py`
- change-log routes: `admin_change_log_routes.py`
- overview/snapshot routes: `admin_overview_snapshot_routes.py`
- route ownership contract: `admin_route_map_contract.py`
- route service factory: `admin_route_services.py`
- legacy service smoke marker: `admin_service_legacy_markers.py`
- `admin_service.py`는 실제 AdminService facade만 유지
- splitStatus: `admin-service-legacy-marker-cleanup-v220`

다음 추천:
- v221 backend admin service facade MRO/import tidy
- `admin_service.py` 상속 줄 가독성 정리
- service split contract/smoke에서 facade 구조를 더 명확히 검증
- 이후 가능하면 route module import order tidy 또는 service contract reporting 개선
