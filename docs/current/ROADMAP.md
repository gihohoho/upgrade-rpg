# Roadmap — v275

## 당분간 보류

게임 콘텐츠 개발은 아직 하지 않습니다.

보류 항목:

- 장비 추가
- 스킬 추가
- 보스 추가
- 필드 추가
- 드랍률/밸런스 조정
- 강화 수치 조정
- 신규 콘텐츠 기획 반영

## 완료 흐름

- v268 프로젝트 구조 점검
- v269 legacy 경로 의존성 자동 목록화
- v270 Vue 기본 shell 생성
- v271 Vue 읽기 전용 API client 준비
- v272 Vue read-only API smoke 화면 연결
- v273 Vue 개발 서버 local CORS 오류 수정
- v274 FastAPI 구조 정리 계획 구체화
- v275 Backend route map 자동 보고서 + Vue read-only route 후보 확정

## v275 결론

- 현재 FastAPI route는 총 27개입니다.
- `GET` route는 15개, `POST` route는 12개입니다.
- Vue 화면에서 이미 자동 확인 중인 route는 `GET /health`, `GET /admin/requirements`입니다.
- 다음 Vue 연결 후보는 `GET /admin/master-data/domains`입니다.
- Preview/Apply/write route는 인증/권한/Write Guard 설계 전까지 Vue 자동 화면에 연결하지 않습니다.

## 다음 작업 후보

### v276 — Vue admin read-only catalog mini panel

목표:

- Vue 관리자 shell에 작은 read-only 카탈로그 점검 패널을 추가합니다.
- 첫 연결은 `GET /api/v1/admin/master-data/domains`만 사용합니다.
- loading/error/empty/success 상태만 확인합니다.
- route path/API response body는 변경하지 않습니다.

주의:

- Preview/Apply/write route 연결 금지
- 인증/interceptor는 아직 구현하지 않음
- DB/Alembic 실제 변경 없음
- env/seed 변경 없음

### v277 — DB/PostgreSQL/Alembic 준비

목표:

- migration/seed/운영 데이터 역할 분리
- DB transaction/rollback snapshot 정책 검토
- 실제 DB 구조 변경은 사용자 승인 후 진행

### v278 — 인증 설계 준비

목표:

- 사용자/관리자 권한 정의
- token 저장 방식 결정
- FastAPI dependency와 Vue route guard 설계
- 기존 Write Guard와의 관계 정리
