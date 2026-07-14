# Roadmap — v293

## 완료 흐름

- v268~v281 구조/route/Vue 관리자 GET 이식
- v282~v289 PostgreSQL/Alembic readiness, runtime, schema equivalence, FLOAT normalization
- v290 backup/restore read-only gate와 분리 DB 경계
- v291 verified custom backup 생성과 TOC/SHA/source snapshot 검증
- v292 빈 restore rehearsal DB 생성 및 source 불변 확인
- v293 isolated target restore와 post-restore 검증 도구 준비

## 현재 단계

사용자가 v293 명령을 실행해 verified dump가 `rpg_game_restore_rehearsal_v290`에만 복원되고 아래가 확인되는지 봅니다.

```txt
target tables/rows: 22 / 748
table별 counts: backup snapshot과 동일
schema: structurally-equivalent / differences=0
source before/after: 동일
```

## 이후 승인 경계

1. restore rehearsal DB 보존 또는 삭제 결정
2. `rpg_game_migration_empty_v290` 빈 DB 생성
3. 최초 Alembic revision 생성·수동 검토
4. 빈 DB upgrade/downgrade 왕복
5. 기존 DB baseline stamp 여부 최종 결정

각 write/drop/migration 단계는 실제 결과를 확인하고 별도 승인합니다.
