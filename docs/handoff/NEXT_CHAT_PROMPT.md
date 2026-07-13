기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

최신 ZIP `rpg_v279_vue_admin_catalog_controls_detail.zip`을 기준으로 작업해주세요.

현재 완료:

- Vue `/admin` health/requirements 상태 확인
- 도메인 목록
- 카탈로그 검색·활성 필터·정렬·페이지네이션
- 선택 row의 read-only detail
- scalar fields/relation hints/sanitized JSON preview
- stale 요청 취소
- requirements `준비 완료` 표시

다음 추천 작업은 `v280 Vue admin read-only relations panel`입니다.

목표:

- 실제 `GET /api/v1/admin/master-data/relations` 응답 구조를 먼저 확인
- 선택 상세 row의 relation groups만 표시
- loading/error/empty/success
- stale 요청 취소
- raw JSON/asset 비표시
- GET만 사용
- 전용 smoke 추가

아직 연결 금지:

- 모든 Preview/Apply/write
- 관계 편집
- 인증/token/interceptor
- DB/Alembic 실제 변경
- env/seed
- 게임 콘텐츠

절대 변경 금지:

- 기존 route path
- API 응답 body
- Write Guard
- 실제 write 로직
- 관리자 Preview/Apply 요청 body
- 기존 Smoke/Contract 의미

명령을 안내할 때 실행 위치와 `.venv` 활성/비활성 여부를 반드시 같이 적어주세요.
새로 설치할 파일/라이브러리/프레임워크와 사용자가 확인할 사항을 빠짐없이 알려주세요.
작업 후 관련 smoke, JS 문법 검사, compileall, core smoke, ZIP 무결성을 확인하고 새 ZIP을 만들어주세요.
