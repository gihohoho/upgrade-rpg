# 다음 추천 단계

## 현재 완료

- v268~v275 구조/route/read-only client 준비
- v276 도메인 목록
- v277 첫 카탈로그
- v278 검색·활성 필터·정렬·페이지네이션
- v279 선택 row 상세 GET

현재 Vue `/admin`에서 사용하는 API:

```txt
GET /api/v1/health
GET /api/v1/admin/requirements
GET /api/v1/admin/master-data/domains
GET /api/v1/admin/master-data/catalog
GET /api/v1/admin/master-data/detail
```

## 현재 보류

- relations GET
- 모든 Preview/Apply/write
- 인증/token/interceptor
- DB/Alembic 실제 변경
- env/seed 변경
- 게임 콘텐츠

## 다음 작업 — v280

`Vue admin read-only relations panel`

추천 범위:

1. 실제 relations 응답 구조 재확인
2. 선택 row의 relation group GET
3. loading/error/empty/success
4. stale 요청 취소
5. raw JSON/asset 비표시 확인
6. 전용 smoke

Preview/Apply/write는 연결하지 않습니다.

## 설치 관련

새 라이브러리/프레임워크는 없습니다.

Vue 의존성이 없는 경우에만:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 필요 없음

```bash
npm install
```
