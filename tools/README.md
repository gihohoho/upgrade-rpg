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
