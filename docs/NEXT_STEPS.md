# Next Steps — v301

## 완료

- schema equivalence differences=0
- verified backup 생성 및 isolated restore rehearsal
- 최초 revision `v295_initial_schema` 수동 검토
- isolated migration DB 왕복 검증 완료

```txt
upgrade head -> downgrade base -> upgrade head
first/second upgrade signatures: identical
```

## 현재 읽기 전용 단계

```bash
python tools/check_postgres_source_baseline_stamp_preflight.py --strict
```

성공 기준:

```txt
result: ready-for-separate-restore-rehearsal-stamp-approval
source: 22 tables / 748 rows / no alembic_version
differences: 0
migration current revision: v295_initial_schema
```

## 그다음 별도 승인

- restore rehearsal DB 전용 `stamp head` guard 준비
- stamp 전후 application table/row/schema 동일성 확인
- `alembic_version` 1 table/1 row만 추가됐는지 확인
- source/migration DB 무변경 확인
- 실제 rehearsal stamp는 사용자 별도 승인

## 계속 금지

원본 DB `upgrade/downgrade/stamp`, 승인 없는 rehearsal stamp, `dropdb`, `.env`, seed, 인증, API body/route/write guard, 게임 콘텐츠 변경.
