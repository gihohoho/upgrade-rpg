# Roadmap — v290

## 완료 흐름

- v268~v275 구조/route/read-only client 준비
- v276~v281 Vue 관리자 GET 이식
- v282~v284 PostgreSQL/Alembic readiness 및 async env 수정
- v285~v287 runtime 비파괴 점검, Windows 출력 보완, baseline 전략 확정
- v288 상세 PostgreSQL/SQLAlchemy schema 비교
- v289 PostgreSQL FLOAT alias 정규화와 handoff 정리
- v290 backup/restore 읽기 전용 gate, 도구 확인, 파일/DB 경계와 검증 계획 확정

## 현재 경계

원본 `rpg_game`은 22개 테이블과 748개 row가 있는 보존 대상입니다.
Alembic 이력은 없으며 기존 데이터 보존형 baseline 후보입니다.

v290은 실제 backup/restore를 실행하지 않았습니다.
사용자 PC에서 schema 차이 0개와 preflight `ready-for-user-approval`을 먼저 확인해야 합니다.

## 다음 작업 — v291 후보

1. 기호 컴퓨터에서 v289 schema checker 실제 결과 수집
2. 차이 0개이면 v290 preflight 실제 결과 수집
3. 선택된 실행 mode가 host인지 `docker-container`인지 확인
4. 사용자에게 backup 생성 한 단계만 승인 요청
5. 승인 후 custom-format dump 생성
6. SHA-256과 파일 크기/존재 확인
7. 이후 restore rehearsal DB 생성은 별도 승인

## backup 이후 별도 승인 단계

- `rpg_game_restore_rehearsal_v290` 생성
- dump restore
- 원본/복원 DB table별 row count 비교
- schema equivalence 비교
- rehearsal DB 삭제
- `rpg_game_migration_empty_v290` 생성
- 최초 Alembic revision 생성/검토
- 빈 DB upgrade/downgrade 검증
- 기존 DB baseline stamp 여부 최종 결정

각 단계는 한 번에 묶지 않습니다.

## 계속 보류

- 게임 콘텐츠 추가/밸런스 조정
- 관리자 Preview/Apply/write Vue 확대
- 인증 구현
- 기존 DB schema/data/env/seed 변경
- Docker volume 삭제
