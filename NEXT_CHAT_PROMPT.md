이전 채팅에서 이어서 진행합니다.

현재 안정 버전은 v216입니다.
업로드할 ZIP은 `rpg_v216_backend_admin_overview_route_facade_split_ready.zip`입니다.

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
- `admin.py`는 router include facade로 축소됨
- master-data routes: `admin_master_data_routes.py`
- change-log routes: `admin_change_log_routes.py`
- overview/snapshot routes: `admin_overview_snapshot_routes.py`
- splitStatus: `admin-route-overview-facade-split-v216`

다음 추천:
- v217 admin.py legacy static-smoke marker cleanup
- 오래된 smoke가 admin.py 주석 대신 실제 route module 파일을 보도록 조정
