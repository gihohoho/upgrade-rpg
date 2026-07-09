# Upgrade RPG v206 패키지

현재 안정 버전: **v206 backend admin config/readiness service split**

새 채팅 인수인계 ZIP: **rpg_v206_backend_admin_config_readiness_service_split_ready.zip**

## 이번 v205~v206에서 정리한 것

v205~v206에서는 백엔드 `AdminService` facade를 더 얇게 만들었습니다. route/schema/API 응답 구조는 그대로 유지하고, facade에 남아 있던 큰 설정값과 마지막 준비 helper만 별도 service로 분리했습니다.

## 핵심 변경

- `backend/app/services/admin/admin_config.py` 추가
- `backend/app/services/admin/admin_readiness_service.py` 추가
- `AdminService`는 route facade로 유지
- master domain/config/allow-list/confirm text/blueprint 설정을 `AdminConfigService`로 이동
- `preview_change`, `_build_readiness`를 `AdminReadinessService`로 이동
- `backend/app/services/admin/__init__.py` export 정리
- 기존 route/schema/API 응답 구조 변경 없음
- DB/env 변경 없음
- v206 전용 smoke test 추가

## 주요 파일

- `backend/app/services/admin_service.py` — route facade 유지
- `backend/app/services/admin/admin_config.py` — v205 신규 config service
- `backend/app/services/admin/admin_readiness_service.py` — v206 신규 readiness service
- `backend/app/services/admin_service_split_contract.py` — splitStatus 갱신
- `src/api/admin-page-readonly.js` — 브라우저 readiness 버전 갱신
- `docs/BACKEND_ADMIN_CONFIG_SERVICE_SPLIT.md` — v205 상세 문서
- `docs/BACKEND_ADMIN_READINESS_SERVICE_SPLIT.md` — v206 상세 문서
- `tools/smoke_backend_admin_config_readiness_service_split.py` — v206 전용 smoke

## 적용 후 확인

관리자 페이지 콘솔:

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v206.backend-admin-config-readiness-service-split
```

```js
checkAdminReadOnlyPageReady().backendConfigServiceSplitReady
```

예상:

```txt
true
```

```js
checkAdminReadOnlyPageReady().backendReadinessServiceSplitReady
```

예상:

```txt
true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
```

예상:

```txt
readiness-extracted-v206
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_config_readiness_service_split.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

## git push 명령

실행 위치: 프로젝트 루트

```bash
git status && git add . && git commit -m "Split backend admin config and readiness services" && git push
```

## 다음 추천

v207은 `AdminService` facade의 legacy smoke marker 문자열을 별도 문서/테스트 기준으로 정리하거나, 백엔드 admin route 파일의 중복 응답 wrapper를 helper로 정리하는 단계가 좋습니다.
