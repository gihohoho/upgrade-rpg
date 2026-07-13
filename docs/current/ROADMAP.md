# Roadmap — v279

## 당분간 보류

- 장비/스킬/보스/필드 추가
- 드랍률/밸런스/강화 수치 변경
- 신규 콘텐츠 기획 반영

## 완료 흐름

- v268 프로젝트 구조 점검
- v269 legacy 경로 의존성 자동 목록화
- v270 Vue 기본 shell
- v271 read-only API client
- v272 안전 GET 상태 화면
- v273 local CORS
- v274 FastAPI 구조 계획
- v275 backend route map
- v276 도메인 목록
- v277 첫 카탈로그
- v278 카탈로그 검색/필터/페이지네이션
- v279 선택 row 상세 GET

## 현재 경계

Vue `/admin`은 도메인, 카탈로그, 상세까지만 GET으로 연결합니다.

계속 보류:

- relations GET
- Preview/Apply/write
- 인증
- DB 구조 변경

## 다음 작업

### v280 — read-only relations

- 선택 상세의 관계 group 조회
- loading/error/empty 상태
- 관련 row 클릭 이동은 응답 구조 확인 후 판단
- GET만 사용

### 이후

- PostgreSQL/Alembic 도입 준비 문서 구체화
- 인증/관리자 권한 설계
- 관리자 Vue 이식 확대
- 게임 Vue 이식
- 배포 직전 안정화
