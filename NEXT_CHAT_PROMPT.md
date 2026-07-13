기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

최신 ZIP `rpg_v277_vue_admin_readonly_catalog_mini_panel.zip`을 기준으로 작업해주세요.

현재 완료:

- Vue `/admin`에서 health, requirements GET 상태 확인
- 마스터 데이터 도메인 목록 표시
- 선택 도메인의 첫 20개 카탈로그 표시
- loading/error/empty/success 상태
- 도메인 변경 시 stale 요청 취소

다음 추천 작업은 `v278 Vue admin catalog query controls`입니다.

목표:

- 검색어
- 활성/비활성 필터
- 이전/다음 페이지
- 기존 `GET /api/v1/admin/master-data/catalog` query만 사용
- 도메인 변경 시 검색/필터/page 초기화
- loading/error/empty/success 유지
- 전용 smoke 추가

아직 연결 금지:

- detail/relations
- 모든 Preview/Apply/write
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
