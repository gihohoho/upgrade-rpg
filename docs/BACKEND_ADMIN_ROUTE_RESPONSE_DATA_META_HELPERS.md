# Backend Admin Route Response Data/Meta Helpers — v212

v212에서는 `backend/app/api/routes/admin.py`의 반복 응답 생성 코드를 아래 두 파일로 분리했다.

- `backend/app/api/routes/admin_response_data_helpers.py`
- `backend/app/api/routes/admin_response_meta_helpers.py`

## 목적

`admin.py`가 service 호출과 route 선언에 집중하도록 만들고, 응답 요약 data와 안내 meta 문구는 helper에서 관리한다.

## 유지한 계약

- API path 변경 없음
- schema 변경 없음
- response envelope 변경 없음
- DB/env 변경 없음

## 검증

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke/contracts/smoke_backend_admin_route_response_data_meta_helpers.py
python -m compileall -q backend/app backend/scripts tools
```
