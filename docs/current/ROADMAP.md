# Roadmap — v284

## 완료 흐름

- v268~v275 구조/route/read-only client 준비
- v276~v281 Vue 관리자 GET 이식
- v282 PostgreSQL/Alembic 정적 readiness 분석
- v283 로컬 설치/사전 조건 checker
- v284 실제 `MissingGreenlet` 근거 async Alembic env 수정

## 현재 경계

Vue `/admin`은 도메인, 카탈로그, 상세, 관계까지 GET으로 연결합니다.
Alembic online 연결 방식은 asyncpg 호환 구조로 바뀌었지만 revision 체계와 DB baseline은 아직 시작하지 않았습니다.

계속 보류:

- Preview/Apply/write
- 관계 편집
- 인증
- DB schema/env/seed 변경
- migration 생성/적용/stamp
- Docker volume 삭제
- 게임 콘텐츠

## 다음 작업 — v285

### 로컬 PostgreSQL 비파괴 런타임 상태 확인

- v284 적용 후 Alembic `history/heads/current` 결과 수집
- `docker compose ps`, `docker volume ls` 확인
- PostgreSQL container/volume 삭제 없이 상태 확인
- `/api/v1/health/db` 실제 결과 확인
- 보존할 기존 DB 데이터 여부 확인
- baseline 전략은 결과 수집 후 결정

## 이후

- 실제 DB 상태에 따라 새 DB baseline 또는 기존 DB baseline 전략 선택
- 사용자 승인 후 첫 migration 생성
- 임시 DB upgrade/downgrade 왕복
- 인증/관리자 권한 설계
- 관리자 Vue 이식 확대
- 게임 Vue 이식
- 배포 직전 안정화
