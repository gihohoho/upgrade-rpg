# Roadmap — v292

## 완료 흐름

- v268~v281 구조/route/Vue 관리자 GET 이식
- v282~v289 PostgreSQL/Alembic readiness, runtime, schema equivalence, FLOAT normalization
- v290 backup/restore read-only gate와 분리 DB 경계
- v291 verified custom backup 생성과 TOC/SHA/source snapshot 검증
- v292 target 존재 여부 확인 후 빈 restore rehearsal DB 생성 도구 준비

## 현재 단계

사용자가 v292 명령을 실행해 `rpg_game_restore_rehearsal_v290`이 빈 DB로 생성되었는지 확인합니다.

## 이후 승인 경계

1. target DB로 verified dump restore
2. source/target table별 row count 비교
3. target schema equivalence 검사
4. restore rehearsal DB 보존 또는 삭제 결정
5. `rpg_game_migration_empty_v290` 빈 DB 생성
6. 최초 Alembic revision 생성·수동 검토
7. 빈 DB upgrade/downgrade 왕복
8. 기존 DB baseline stamp 여부 최종 결정

각 write/drop/migration 단계는 실제 결과를 확인하고 별도 승인합니다.
