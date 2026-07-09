# Backend Ready Notes — v199.1

현재 v199 기준으로 프론트 관리자 JS 주요 분리는 완료되어 있고, 백엔드 `AdminService`도 첫 실제 분리를 시작했습니다.

## v199 백엔드 변경

- `backend/app/services/admin/` 패키지 추가
- `backend/app/services/admin/admin_overview_snapshots_service.py` 추가
- overview/save snapshots 관련 메서드를 `AdminOverviewSnapshotsService`로 이동
- `AdminService`는 route가 import하는 facade로 계속 유지

## Backend 영향

이번 변경은 백엔드 service 내부 분리입니다.

- DB schema 변경 없음
- seed 변경 없음
- API route 변경 없음
- schema 변경 없음
- `.env` 변경 없음

## 유지된 백엔드 관련 기능

- admin overview API 유지
- save snapshot list API 유지
- master catalog/detail/API verify 유지
- guarded edit apply 유지
- change log rollback/create-delete/restore 유지
- create lifecycle batch check 유지
- admin write dev key guard 유지

## v199.1 hotfix 내용

- `/api/v1/admin/save-snapshots` 500 오류 수정
- `_count_filled_items` staticmethod 누락 복구
- snapshot summary runtime smoke 추가

## 검증

- `python -m compileall -q backend/app` 통과
- `python tools/smoke_backend_admin_overview_snapshots_service_split.py` 통과
- `bash tools/run_smoke_core.sh` 통과
- `bash tools/run_smoke_all.sh` 통과
