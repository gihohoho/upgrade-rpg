# Backend Ready — v238

현재 안정 버전: `v239.2.backend-admin-schema-model-shared-collector-hotfix`

## 백엔드 상태

- Admin request schema/model 계약 유지
- Admin request field constraint/default/required/model-config 계약 추가
- `backend/app/services/admin_service_split_contract.py` splitStatus: `admin-schema-field-constraint-contract-v238`
- 관리자 route path/API 응답 body 구조 변경 없음
- DB/env 변경 없음

## 핵심 보장

- OpenAPI에 노출되는 Admin request schema 11개와 route body model 연결을 검증합니다.
- `domain` 1~80자, `reason` 최대 500자, `confirmText` 최대 80자 제약을 고정합니다.
- 편집 request의 `id >= 1` 제약을 고정합니다.
- preview의 `dryRun=true`, apply의 `dryRun=false` 기본값을 고정합니다.
- required 필드 목록과 alias 기반 OpenAPI 직렬화가 바뀌면 smoke가 실패합니다.
- `populate_by_name`, `str_strip_whitespace`, alias/name 입력 허용 동작을 검증합니다.

## 관련 핵심 파일

- `backend/app/api/routes/admin_schema_model_contract.py`
- `backend/app/api/routes/admin_schema_field_constraint_contract.py`
- `tools/smoke_backend_admin_schema_model_contract.py`
- `tools/smoke_backend_admin_schema_field_constraint_contract.py`
- `backend/app/schemas/admin.py`

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_schema_field_constraint_contract.py
python tools/smoke_backend_admin_schema_model_contract.py
python -m compileall -q backend/app backend/scripts tools
```
