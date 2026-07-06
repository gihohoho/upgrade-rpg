# tools

현재 폴더는 백엔드 분리 준비 과정에서 코드/스타일 검증에 사용한 보조 스크립트를 넣는 공간입니다.

운영 코드에는 직접 포함되지 않습니다.


## 현재 주요 도구

```txt
check_backend_ready.py        로컬 백엔드/Docker/PostgreSQL 준비 상태 점검
extract_seed_data.js          현재 JS 마스터 데이터를 JSON seed로 추출
smoke_seed_extraction.js      생성된 seed JSON 기본 검증
smoke_action_results.js       Action Result 구조 검증
smoke_api_response_contract.js API 응답 계약 검증
smoke_backend_foundation.js   backend/ 뼈대 파일 존재 검증
smoke_master_data_parity_checker.py  v086 parity checker 정적 검증
smoke_nullable_skill_proc_rate.py  v087 nullable skill procRate 검증
```

## seed 추출

프로젝트 루트에서 실행합니다.

```bash
node tools/extract_seed_data.js
node tools/smoke_seed_extraction.js
```


## frontend master-data bridge

프로젝트 루트에서 실행합니다.

```bash
node tools/smoke_frontend_master_data_bridge.js
```

브라우저에 추가된 `RpgGameApi`, `RpgMasterDataBridge`, `checkBackendMasterData()` 로딩 순서와 기본 동작을 검증합니다.


## master-data parity checker

프로젝트 루트에서 정적 검사를 실행합니다.

```bash
python tools/smoke_master_data_parity_checker.py
```

실제 seed/API parity 검사는 FastAPI 서버를 켠 뒤 backend 폴더에서 실행합니다.

```bash
python scripts/check_master_data_parity.py
python scripts/check_master_data_parity.py --include-assets
```


## nullable skill procRate

프로젝트 루트에서 실행합니다.

```bash
python tools/smoke_nullable_skill_proc_rate.py
```

`lightsabre`처럼 기본 발동확률이 없는 스킬의 `procRate`가 `0`으로 바뀌지 않고 `null`로 보존되는지 확인합니다.

## v088 frontend master-data adapter

위치: 프로젝트 루트

```bash
node tools/smoke_master_data_adapter.js
```

FastAPI master-data 응답을 기존 브라우저 게임 데이터와 비슷한 형태로 변환할 수 있는지 확인합니다.

## v089

- `smoke_master_data_runtime_switch.js`: 백엔드 master-data 런타임 스위치 파일과 index.html 로딩 순서를 정적으로 검사한다.

## v090 backend master-data runtime validator

위치: 프로젝트 루트

```bash
node tools/smoke_master_data_runtime_validator.js
```

브라우저 Console에서 백엔드 master-data 주입 상태와 핵심 화면 요소를 확인할 수 있습니다.

```js
checkBackendMasterDataRuntimeIntegrity({ requireBackendMode: true });
getBackendMasterDataRuntimeDebugSnapshot();
```

## v091 backend master-data browser checklist

위치: 프로젝트 루트

```bash
node tools/smoke_master_data_browser_checklist.js
```

브라우저 Console에서 백엔드 master-data 모드의 실제 화면 점검 리포트를 생성할 수 있습니다.

```js
runBackendMasterDataBrowserChecklist();
printBackendMasterDataManualChecklist();
```
### `smoke_master_data_auto_boot_policy.js`

위치: **프로젝트 루트**

```bash
node tools/smoke_master_data_auto_boot_policy.js
```

백엔드 master-data 자동 부트 정책, timeout 처리, 로딩 순서가 들어갔는지 확인합니다.


- `node tools/smoke_field_zone_asset_fallback.js`: 백엔드 master-data 모드에서 필드 이미지가 제외되어도 정적 JS 이미지 또는 안전한 기본 이미지로 보정되는지 확인합니다.

## v099 save snapshot bridge checks

Run from the project root:

```bash
python tools/smoke_save_snapshot_api_structure.py
node tools/smoke_save_data_bridge.js
```

Run from the backend folder while FastAPI is running:

```bash
python scripts/check_save_snapshot_api.py
```

## v100 save data dual-write

위치: **프로젝트 루트**

```bash
node tools/smoke_save_data_dual_write.js
```

수동 저장 버튼이 기존 localStorage 저장 후 백엔드 save snapshot API에도 저장을 시도하도록 연결되었는지 정적으로 검사합니다.

- `smoke_save_data_dev_badge.js`: SAVE DATA 개발자 배지 구조와 로딩 순서를 확인합니다.
