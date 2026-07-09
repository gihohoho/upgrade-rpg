이전 채팅에서 이어서 할게. 첨부한 zip은 v206 `backend admin config/readiness service split` 완료본이야.

중요한 진행 원칙:
- 나는 코딩/터미널/경로에 익숙하지 않으니까, 명령어를 줄 때는 반드시 실행 위치를 먼저 적어줘.
- git 명령은 가능하면 `git status && git add . && git commit ... && git push`처럼 한 번에 복사 가능한 한 코드 블록으로 줘.
- 오류가 나면 그때 고치면 되니까, 네 판단으로 과감하게 다음 단계 진행해도 돼.
- 안정적으로 여러 단계를 묶을 수 있으면 묶어서 진행해도 돼.
- route/schema/API 응답/DB/env는 꼭 필요한 경우가 아니면 변경하지 마.

현재 완료:
- v198 backend admin service split contract
- v199.1 overview/save snapshots service split + hotfix
- v200 master catalog/detail/relations service split
- v201 create lifecycle service split
- v202 change logs/detail/rollback service split
- v203 edit draft preview/apply service split
- v204 shared utils service split
- v205 config service split
- v206 readiness service split

v206 확인값:
```js
checkAdminReadOnlyPageReady().version
// v206.backend-admin-config-readiness-service-split

checkAdminReadOnlyPageReady().backendConfigServiceSplitReady
// true

checkAdminReadOnlyPageReady().backendReadinessServiceSplitReady
// true

getAdminBackendServiceSplitContractReadiness().splitStatus
// readiness-extracted-v206
```

검증 명령:

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_config_readiness_service_split.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

다음 추천:
1. v207 backend admin route response helper cleanup
2. 또는 legacy smoke marker cleanup
3. route/schema/API/DB/env 변경 없이 진행
4. v207 전용 smoke 추가
5. core smoke/compileall 검증
