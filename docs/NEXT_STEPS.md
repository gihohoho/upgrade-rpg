# Next Steps — v304

## 완료

- PostgreSQL schema equivalence differences=0
- verified backup과 isolated restore rehearsal
- 최초 revision `v295_initial_schema` 자동/수동 검토
- isolated migration DB upgrade → downgrade base → upgrade 왕복 검증
- v301 source preflight 통과
- v302 restore rehearsal stamp 통과
- v303 restore rehearsal post-check 및 v302 report 검증 통과

## 현재 읽기 전용 단계

```bash
python tools/stamp_postgres_source_database.py --inspect
```

성공 기준:

```txt
result: ready-for-separate-source-baseline-stamp-execution-approval
target: rpg_game
revision: v295_initial_schema
source application tables/rows: 22/748
source/rehearsal schema/data digest: identical
backup/revision/rehearsal report/migration endpoint: verified
no mutation executed
```

## 그다음 별도 승인

1. 기호님이 v304 `--inspect` 전체 결과 공유
2. exact source target/revision/backup SHA/rehearsal result 재확인
3. 실제 source `stamp head` 실행 여부 별도 승인
4. 실행 후 source application schema/data digest 동일 확인
5. `alembic_version` 1 table/1 row와 revision만 추가 확인
6. rehearsal/migration DB 무변경 확인
7. source post-check와 v304 local execution report 검증
8. 그 뒤 Alembic 운영 기준 문서화 및 다음 DB 단계 검토

## 계속 금지

승인 없는 source stamp, source upgrade/downgrade, rehearsal stamp 재실행, migration DB 추가 변경, DB create/drop/restore, Docker volume 삭제, `.env`, seed, 인증, API body/route/write guard, 게임 콘텐츠 변경.
