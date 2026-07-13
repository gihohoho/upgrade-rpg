# Roadmap — v271

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

## 다음 작업 후보

### v272 — Vue read-only API smoke 화면 연결

목표:

- Vue shell에서 실제 GET API를 아주 작게 호출합니다.
- 처음에는 `/admin/requirements`, `/health`, `/game/save-slots`처럼 안전한 조회 API만 후보로 둡니다.
- loading/error/success 표시 구조를 먼저 만듭니다.
- write/Preview/Apply는 계속 제외합니다.

주의:

- API route path 변경 금지
- API response body 변경 금지
- 인증/interceptor는 아직 구현하지 않음
- `.env`는 아직 만들지 않음

### v273 — Backend 구조 정리 계획

목표:

- FastAPI route/service/schema/model/repository 역할 재정의
- 기존 route path 유지 방식 정리
- contract/readiness 영향 분석

### v274 — DB/PostgreSQL/Alembic 준비

목표:

- migration/seed/운영 데이터 역할 분리
- DB transaction/rollback snapshot 정책 검토
- 실제 DB 구조 변경은 사용자 승인 후 진행

### v275 — 인증 설계 준비

목표:

- 사용자/관리자 권한 정의
- token 저장 방식 결정
- FastAPI dependency와 Vue route guard 설계
- 기존 Write Guard와의 관계 정리
