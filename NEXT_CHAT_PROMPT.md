이전 채팅에서 이어서 할게. 첨부한 zip은 v210 `backend admin route params/error helpers` 완료본이야.

현재 사용자는 게임 프로젝트에서 코딩을 잘 모르는 기호로 보고, 설명은 쉽게 해줘. 단, 코드는 과감하게 정리해도 돼. 안정성이 중요한 작업은 천천히 smoke test를 추가하면서 진행해줘.

현재 완료 상태:
- v199 overview/save snapshots service split
- v200 master catalog service split
- v201 create lifecycle service split
- v202 change log service split
- v203 edit draft service split
- v204 shared utils service split
- v205 config service split
- v206 readiness service split
- v207~v208 admin route response helper cleanup
- v209~v210 admin route params/error helpers cleanup

v210 확인값:
```js
checkAdminReadOnlyPageReady().version
// v210.backend-admin-route-params-error-helpers

checkAdminReadOnlyPageReady().backendRouteParamsReady
// true

checkAdminReadOnlyPageReady().backendRouteErrorHelperReady
// true

getAdminBackendServiceSplitContractReadiness().splitStatus
// admin-route-params-errors-v210
```

v210 변경 핵심:
- `backend/app/api/routes/admin_route_params.py` 추가
- `backend/app/api/routes/admin_route_error_helpers.py` 추가
- `backend/app/api/routes/admin.py`의 반복 Depends/Query 기본값을 helper 상수로 정리
- `/admin/change-logs` route-level fallback payload 생성을 helper로 분리
- route/schema/API/DB/env 변경 없음
- `tools/smoke_backend_admin_route_params_error_helpers.py` 추가

검증 완료:
```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_route_params_error_helpers.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

다음 추천:
- v211 admin route response data builder 준비 또는 route submodule split 준비 smoke 강화
- 바로 admin.py를 여러 route 파일로 쪼개는 것은 static smoke 영향이 커서 조심
- 먼저 route contract smoke를 더 강하게 하고, data summary helper 같은 반복을 안전하게 정리하는 것을 추천

중요 사용자 선호:
- 터미널 명령을 안내할 때는 어느 위치/폴더에서 실행하는지 먼저 적어줘.
- git 명령은 한 번에 복사 가능하게 `git status && git add . && git commit ... && git push` 한 코드 블록으로 제공해줘.
