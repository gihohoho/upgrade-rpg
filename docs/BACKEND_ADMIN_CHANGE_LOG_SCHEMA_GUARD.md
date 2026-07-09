# Backend Admin Change Log Schema Guard

버전: **v201.2 admin change log schema guard hotfix**

## 해결한 문제

관리자 페이지에서 아래 요청이 500으로 실패할 수 있던 문제를 보완했습니다.

```txt
GET /api/v1/admin/change-logs?limit=20&sort=created_desc
```

로컬 Docker PostgreSQL 볼륨이 오래된 상태면 현재 코드가 기대하는 `admin_change_logs` 테이블 또는 컬럼이 DB에 아직 없을 수 있습니다. 이 경우 기존 코드는 변경 이력 목록 조회 시 바로 DB 오류가 발생했습니다.

## 수정 내용

- `AdminService._ensure_admin_change_log_schema()` 추가
- 변경 이력 목록/상세/되돌리기 미리보기 진입 전에 `admin_change_logs` 테이블과 핵심 컬럼을 보정
- create/edit/rollback apply에서 change log를 쓰기 전에 같은 schema guard를 먼저 실행
- `tools/smoke_backend_admin_change_log_schema_guard.py` 추가
- `tools/run_smoke_core.sh`에 새 smoke 포함

## 의도

이 프로젝트는 아직 로컬 개발 단계라 전체 Alembic migration 체계를 본격 적용하기 전입니다. 그래서 기존 로컬 DB를 유지한 채 ZIP만 교체하면 코드와 DB 스키마가 어긋날 수 있습니다.

이번 guard는 로컬 개발 편의용 안전장치입니다. DB reset 없이도 변경 이력 화면이 500으로 죽지 않게 하는 것이 목표입니다.

## 주의

- `.env` 변경 없음
- seed 재실행 필요 없음
- 기존 master-data row 삭제 없음
- 기존 save snapshot 삭제 없음
- 정식 운영 migration 대체용은 아님
