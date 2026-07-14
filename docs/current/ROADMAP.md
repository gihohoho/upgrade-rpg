# Roadmap — v298

## 완료 흐름

- v268~v281 구조/route/Vue 관리자 GET 이식
- v282~v289 PostgreSQL/Alembic readiness, runtime, schema equivalence, FLOAT normalization
- v290 backup/restore read-only gate
- v291 verified custom backup 생성
- v292 빈 restore rehearsal DB 생성
- v293 isolated restore 22 tables / 748 rows / differences=0
- v294 empty migration test DB 생성
- v295~v297 최초 revision 생성 과정의 placeholder/op.f false positive 복구
- v297 실제 revision 생성 및 자동 검토 성공
- v298 exact revision 수동 교차 검토와 isolated upgrade guard 준비

## 현재 단계

```bash
python tools/upgrade_postgres_migration_test_database.py --inspect
```

읽기 전용 결과가 `ready-for-separate-upgrade-approval`일 때 별도 사용자 승인을 받습니다.

## 이후 승인 경계

1. isolated migration DB `upgrade head`
2. 22 model tables + `alembic_version`, differences=0 확인
3. migration DB downgrade 별도 승인
4. downgrade 후 placeholder/empty 상태 확인
5. 재-upgrade 별도 승인 및 왕복 검증
6. source DB baseline stamp 여부 최종 검토
7. 필요할 때만 rehearsal/migration DB drop 별도 승인

각 upgrade/downgrade/stamp/drop은 실제 결과를 확인한 뒤 별도 승인합니다.
