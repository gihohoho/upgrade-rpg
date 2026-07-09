이전 채팅에서 이어서 할게. 첨부한 zip은 v208 `backend admin route response helper` 완료본이야.

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

v208 확인값:
```js
checkAdminReadOnlyPageReady().version
// v208.backend-admin-route-response-helper

checkAdminReadOnlyPageReady().backendRouteResponseHelperReady
// true

getAdminBackendServiceSplitContractReadiness().splitStatus
// route-response-helper-v208
```

v208 변경 핵심:
- `backend/app/api/routes/admin_response_helpers.py` 추가
- `backend/app/api/routes/admin.py`의 `ok_response()` 직접 호출을 `admin_ok_response()`로 변경
- route/schema/API/DB/env 변경 없음
- `tools/smoke_backend_admin_route_response_helper.py` 추가

검증 완료:
```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_route_response_helper.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

다음 추천:
- v209 admin route query dependency cleanup 또는 route submodule split 준비
- 바로 admin.py를 여러 route 파일로 쪼개는 것은 static smoke 영향이 커서 조심
- 먼저 route contract smoke를 더 강하게 하고, query/default/sort 같은 반복을 안전하게 정리하는 것을 추천

중요 사용자 선호:
- 터미널 명령을 안내할 때는 어느 위치/폴더에서 실행하는지 먼저 적어줘.
- git 명령은 한 번에 복사 가능하게 `git status && git add . && git commit ... && git push` 한 코드 블록으로 제공해줘.
