# Backend Ready Notes — v216

현재 안정 버전: **v216 backend admin route overview facade split**

## 변경 요약

- `admin_overview_snapshot_routes.py` 추가
- `/requirements`, `/overview`, `/save-snapshots`, `/change-preview` route 이동
- `admin.py`는 master-data/change-log/overview-snapshot router include facade로 축소
- route path/schema/API 응답 구조 변경 없음
- DB/env 변경 없음

## 서버 재실행

실행 위치: backend 폴더

```bash
uvicorn app.main:app --reload
```

DB reset/seed 재실행은 필요 없습니다.
