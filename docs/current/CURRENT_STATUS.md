# 현재 상태

- 관리자 readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- 정리 번들: `v250.2 docs/smoke/registry/preview integration`

## 이번 정리에서 완료

- 문서: `docs/current`, `docs/contracts`, `docs/handoff`, `docs/archive`로 역할 분리
- Smoke: `tools/smoke/frontend|contracts|backend|game`로 분류
- 계약 자동 동기화: `tools/contracts/sync_admin_contract_registry.py`
- Preview 공통 응답 선택 필드: `unifiedDiff`, `unifiedDiffCount`, `rollbackSnapshot`, `previewSchemaVersion`
- 생성/수정/rollback/create-delete/restore Preview UI에 공통 Diff 표시

DB/env/seed/인증/write guard/기존 route와 기존 응답 필드는 변경하지 않았습니다.
