# Next Steps — v300

## 완료

- schema equivalence differences=0
- verified custom backup 생성
- isolated restore rehearsal 22 tables / 748 rows / differences=0
- 최초 revision `v295_initial_schema` 생성 및 수동 검토 통과
- isolated migration DB 첫 `upgrade head` 실제 성공
- isolated migration DB `downgrade base` 실제 성공
- 현재 migration DB는 빈 `alembic_version` placeholder

## 현재 승인된 단계

```bash
python tools/reupgrade_postgres_migration_test_database.py --inspect && python tools/reupgrade_postgres_migration_test_database.py --execute
```

성공 기준:

```txt
result: migration-test-database-roundtrip-upgraded-and-verified
public tables: 23
current revision: ['v295_initial_schema']
differences: 0
first/second upgrade signatures: identical
source/rehearsal preserved: 22/748
```

## 그다음 별도 승인

- 왕복 결과를 유지한 채 source DB baseline stamp preflight 설계
- source DB의 exact schema/row/revision 부재 상태 재검사
- stamp 적용 전 backup/checksum 재검증
- 실제 source DB `stamp`는 별도 명시 승인

## 계속 금지

원본 DB `upgrade/downgrade/stamp`, `dropdb`, `.env`, seed, 인증, API body/route/write guard, 게임 콘텐츠 변경.
