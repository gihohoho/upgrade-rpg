# Current Status — v281

## 현재 기준

- 최신 작업: `v281.vue-admin-related-detail-navigation`
- 기준 ZIP: `rpg_v281_vue_admin_readonly_relations_navigation.zip`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## v276~v281 완료

Vue 관리자 shell의 read-only 이식을 여섯 단계 진행했습니다.

- v276: 도메인 목록
- v277: 첫 카탈로그
- v278: 검색·활성 상태·정렬·페이지네이션
- v279: 안전한 상세 조회
- v280: 관계 그룹 조회
- v281: 연관 row 상세 이동과 이전 상세 돌아가기

## 현재 Vue `/admin` 실제 GET

- `GET /api/v1/health`
- `GET /api/v1/admin/requirements`
- `GET /api/v1/admin/master-data/domains`
- `GET /api/v1/admin/master-data/catalog`
- `GET /api/v1/admin/master-data/detail`
- `GET /api/v1/admin/master-data/relations`

## 안전 경계

- 모든 신규 연결은 GET만 사용
- 관계 그룹당 `limit=20`
- detail/relations 요청은 `AbortController`로 stale 요청 취소
- raw JSON/asset 원본 비표시
- 연관 row 이동 기록은 Vue 메모리에만 보관
- 관계 편집, Preview/Apply/write 미연결

## 변경하지 않은 것

- DB 구조, `.env`, seed, 인증
- route path, API 응답 body
- Write Guard, 실제 write 로직
- Preview/Apply 요청 body
- 기존 smoke/contract 의미
- 게임 콘텐츠

## 설치

v280~v281에서 새 라이브러리나 프레임워크는 없습니다.

`frontend/vue-app/node_modules`가 없을 때만:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 필요 없음 / 꺼져 있어도 됨

```bash
npm install
```

## 사용자 확인

`http://127.0.0.1:5173/admin`에서 관계 그룹, 연관 row 상세 이동, `이전 상세로`, 선택 해제, 콘솔 오류 여부를 확인합니다.

## 다음 추천 단계

`v282 PostgreSQL/Alembic 도입 준비 상세 계획`

실제 DB/env를 변경하지 않고 현재 모델·설정·마이그레이션 파일의 도입 순서와 검증 체크리스트를 문서화합니다.
