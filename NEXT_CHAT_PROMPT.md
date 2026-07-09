이전 채팅에서 이어서 할게. 첨부한 zip은 v214 `backend admin route module split` 완료본이야.

나는 코딩을 모르는 기호고, Vue/FastAPI 게임 프로젝트를 관리자페이지 중심으로 정리 중이야. 설명은 한국어로 쉽게 해줘.

중요한 습관:
- 터미널 명령은 항상 실행 위치를 먼저 알려줘.
- git 명령은 `git status && git add . && git commit ... && git push` 형태로 한 번에 복사 가능하게 줘.
- 한 번에 여러 단계 과감하게 해도 되지만, 안정성이 중요한 작업은 천천히 해줘.

v214 확인값:

```js
checkAdminReadOnlyPageReady().version
// v214.backend-admin-route-module-split
```

```js
checkAdminReadOnlyPageReady().backendRouteModuleSplitReady
// true
```

```js
checkAdminReadOnlyPageReady().backendRouteMasterDataModuleReady
// true
```

```js
checkAdminReadOnlyPageReady().backendRouteChangeLogModuleReady
// true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
// admin-route-module-split-v214
```

v214 변경 핵심:
- `backend/app/api/routes/admin_master_data_routes.py` 추가
- `backend/app/api/routes/admin_change_log_routes.py` 추가
- `admin.py`를 router include facade로 축소
- API path/schema/envelope/DB/env 변경 없음
- route module split smoke, seed smoke, compileall 통과

다음 단계는 v215로, 남은 overview/save-snapshots/change-preview route를 별도 module로 분리해서 `admin.py`를 include facade만 남기는 작업을 추천해줘.
