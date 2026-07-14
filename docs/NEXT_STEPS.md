# Next Steps — v302

## 완료

- schema equivalence differences=0
- verified backup 생성 및 isolated restore rehearsal
- 최초 revision `v295_initial_schema` 수동 검토
- isolated migration DB 왕복 검증 완료
- v301 source baseline stamp read-only preflight 사용자 실제 통과

```txt
upgrade head -> downgrade base -> upgrade head
first/second upgrade signatures: identical
v301 result: ready-for-separate-restore-rehearsal-stamp-approval
```

## 현재 읽기 전용 단계

```bash
python tools/stamp_postgres_restore_rehearsal_database.py --inspect
```

성공 기준:

```txt
result: ready-for-separate-restore-rehearsal-stamp-execution-approval
target: rpg_game_restore_rehearsal_v290
revision: v295_initial_schema
application tables/rows: 22/748
schema digest: collected
data digest: collected
no mutation executed
```

## 그다음 별도 승인

1. 기호님이 v302 `--inspect` 전체 결과 공유
2. exact target/revision/signature 결과 확인
3. 실제 rehearsal `stamp head` 실행 여부 별도 승인
4. 실행 후 application schema/data digest 동일 확인
5. `alembic_version` 1 table/1 row와 revision만 추가 확인
6. source/migration DB digest 동일 확인
7. 그 뒤에만 원본 source stamp guard 설계 여부 검토

## 계속 금지

원본 DB `upgrade/downgrade/stamp`, 승인 없는 rehearsal stamp, migration DB 추가 변경, `dropdb`, `.env`, seed, 인증, API body/route/write guard, 게임 콘텐츠 변경.
