# Backend Ready Notes — v220

현재 안정 버전: **v220 backend admin route service dependency + legacy marker cleanup**

## 변경 요약

- `admin_route_services.py` 추가
- 관리자 route module 3개가 `create_admin_service()` helper를 통해 `AdminService` facade 생성
- route module에서 `AdminService()` 직접 생성 제거
- `admin_service_legacy_markers.py` 추가
- `admin_service.py`의 긴 legacy marker 문자열 제거
- `admin_service.py`는 실제 facade만 유지
- route path/schema/API 응답 구조 변경 없음
- DB/env 변경 없음

## 서버 재실행

실행 위치: backend 폴더

```bash
uvicorn app.main:app --reload
```

DB reset/seed 재실행은 필요 없습니다.
