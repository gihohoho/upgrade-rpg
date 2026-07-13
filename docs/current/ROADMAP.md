# Roadmap — v281

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
- v278 검색/필터/페이지네이션
- v279 상세 GET
- v280 관계 그룹 GET
- v281 연관 row 상세 이동/뒤로가기

## 현재 경계

Vue `/admin`은 도메인, 카탈로그, 상세, 관계까지 GET으로 연결합니다.

계속 보류:

- 관계 편집
- Preview/Apply/write
- 인증
- DB 구조/env/seed 변경

## 다음 작업

### v282 — PostgreSQL/Alembic 준비 계획

- 현재 model/session/config/Alembic 구조 분석
- 전환 순서와 rollback 체크리스트
- 실제 환경에서 실행할 사전 점검 명령 정의
- DB와 `.env`는 변경하지 않음

### 이후

- 사용자 승인 후 PostgreSQL/Alembic 단계별 도입
- 인증/관리자 권한 설계
- 관리자 Vue 이식 확대
- 게임 Vue 이식
- 배포 직전 안정화
