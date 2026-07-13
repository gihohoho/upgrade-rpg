기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

최신 ZIP `rpg_v281_vue_admin_readonly_relations_navigation.zip`을 기준으로 작업해주세요.

현재 완료:

- Vue `/admin` health/requirements
- 도메인 목록
- 카탈로그 검색·필터·정렬·페이지네이션
- 선택 row read-only detail
- read-only relations groups
- 연관 row 상세 이동과 이전 상세 돌아가기
- stale 요청 취소
- raw JSON/asset 비표시

다음 추천 작업은 `v282 PostgreSQL/Alembic 도입 준비 상세 계획`입니다.

목표:

- 현재 SQLAlchemy model/base/session/config 분석
- Alembic 현재 파일과 실행 경로 분석
- PostgreSQL 전환 순서와 rollback 계획
- 실제 환경에서 먼저 확인할 명령과 결과 기준 정의
- 문서/report/smoke 추가
- 실제 DB, env, seed는 변경하지 않음

아직 연결/변경 금지:

- 모든 Preview/Apply/write
- 관계 편집
- 인증/token/interceptor
- DB/Alembic 실제 적용
- env/seed
- 게임 콘텐츠

명령 안내 시 실행 위치와 `.venv` 활성/비활성 여부를 반드시 같이 적어주세요. 설치 파일/라이브러리/프레임워크와 사용자가 확인할 사항도 빠짐없이 알려주세요.

작업 후 관련 smoke, JS 문법 검사, compileall, core smoke, ZIP 무결성을 확인하고 새 ZIP을 만들어주세요.
