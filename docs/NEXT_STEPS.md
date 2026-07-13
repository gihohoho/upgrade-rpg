# 다음 추천 단계

## 현재 완료

- v268~v275 구조/route/read-only client 준비
- v276 도메인 목록
- v277 첫 카탈로그
- v278 검색·필터·페이지네이션
- v279 상세 GET
- v280 관계 그룹 GET
- v281 연관 row 상세 이동/뒤로가기

현재 Vue `/admin`에서 health, requirements, domains, catalog, detail, relations GET을 사용합니다.

## 계속 보류

- 관계 편집
- 모든 Preview/Apply/write
- 인증/token/interceptor
- DB/Alembic 실제 변경
- `.env`/seed 변경
- 게임 콘텐츠

## 다음 작업 — v282

`PostgreSQL/Alembic 도입 준비 상세 계획`

추천 범위:

1. 현재 SQLAlchemy model/base/session 구조 재점검
2. 기존 Alembic 파일과 실행 가능 상태 점검
3. SQLite/현재 DB 의존 지점 목록화
4. PostgreSQL 전환 순서와 rollback 계획
5. 환경변수 이름과 비밀값 관리 계획만 문서화
6. 실제 DB/env/seed 변경 금지
7. 전용 report/smoke 추가

## 설치 관련

v280~v281에서 새 라이브러리/프레임워크는 없습니다.
Vue `node_modules`가 없다면 `frontend/vue-app`에서 `.venv` 없이 `npm install`을 한 번 실행합니다.
