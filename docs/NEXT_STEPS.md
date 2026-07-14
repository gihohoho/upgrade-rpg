# Next Steps — v299

## 완료

- schema equivalence differences=0
- verified custom backup 생성
- isolated restore rehearsal 22 tables / 748 rows / differences=0
- 최초 revision `v295_initial_schema` 생성 및 수동 검토 통과
- isolated migration DB `upgrade head` 실제 성공
- migration DB current revision `v295_initial_schema`
- migration DB schema differences=0
- source/rehearsal DB 작업 전후 동일

## 현재 승인된 단계

```bash
python tools/downgrade_postgres_migration_test_database.py --execute
```

성공 기준:

```txt
result: migration-test-database-downgraded-to-base-and-verified
public tables: ['alembic_version']
application tables remaining: 0
recorded revisions: []
differences: 22
source/rehearsal preserved: 22/748
```

## 그다음 별도 승인

- 같은 migration DB에서 다시 `upgrade head`
- 두 번째 upgrade 결과가 첫 번째와 동일한지 왕복 재현성 비교
- 왕복 통과 후 기존 source DB에 baseline `stamp`를 적용할지 전략 검토

## 계속 금지

원본 DB `upgrade/stamp`, `dropdb`, `.env`, seed, 인증, API body/route/write guard, 게임 콘텐츠 변경.
