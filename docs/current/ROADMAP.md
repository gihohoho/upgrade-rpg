# Roadmap — v277

## 당분간 보류

게임 콘텐츠 개발은 아직 하지 않습니다.

- 장비/스킬/보스/필드 추가
- 드랍률/밸런스/강화 수치 변경
- 신규 콘텐츠 기획 반영

## 완료 흐름

- v268 프로젝트 구조 점검
- v269 legacy 경로 의존성 자동 목록화
- v270 Vue 기본 shell 생성
- v271 Vue read-only API client 준비
- v272 안전 GET 상태 화면
- v273 local CORS 수정
- v274 FastAPI 구조 계획
- v275 backend route map
- v276 Vue 관리자 도메인 목록
- v277 Vue 관리자 첫 카탈로그 페이지

## 현재 경계

Vue `/admin`은 아래 GET만 실제 호출합니다.

- `/health`
- `/admin/requirements`
- `/admin/master-data/domains`
- `/admin/master-data/catalog`

Preview/Apply/write, 인증, DB 구조 변경은 아직 하지 않습니다.

## 다음 작업

### v278 — catalog query controls

- 검색어
- 활성/비활성 필터
- 페이지네이션
- 안전한 GET query만 사용
- stale request 취소 유지

### v279 — read-only detail 준비

- 선택 row의 detail GET
- 상세 loading/error/empty 처리
- relations는 별도 단계

### 이후

- PostgreSQL/Alembic 도입 준비 문서 구체화
- 인증/관리자 권한 설계
- 관리자 Vue 이식 확대
- 게임 Vue 이식
- 배포 직전 안정화
