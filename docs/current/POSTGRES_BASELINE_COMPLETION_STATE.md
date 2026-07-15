# PostgreSQL / Alembic baseline completion state — v305

## 결론

사용자 PC에서 최초 PostgreSQL/Alembic baseline 전체 절차가 완료됐습니다.

```txt
classification: alembic-managed-baseline-complete
source rpg_game: 23 public tables / 749 rows
source application data: 22 tables / 748 rows preserved
source current revision: v295_initial_schema
restore rehearsal: 23/749 / v295_initial_schema / v302 report verified
migration test DB: 23/1 / v295_initial_schema / differences=0
v304 source execution report: verified
```

baseline stamp 전후 application schema/data digest는 동일합니다.

```txt
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
```

## v305 읽기 전용 고정 도구

```txt
tools/check_postgres_baseline_completion_state.py
tools/smoke/backend/smoke_postgres_baseline_completion_state.py
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_baseline_completion_state.py --strict
```

이 도구는 다음을 한 번에 읽기 전용으로 검증합니다.

- source가 `rpg_game`이며 23/749, application 22/748인지
- source current revision이 정확히 `v295_initial_schema`인지
- source runtime classification이 `alembic-managed`인지
- v304 source 실행 보고서가 verified인지
- rehearsal이 23/749이고 v302 실행 보고서가 verified인지
- migration DB가 23/1의 검증된 왕복 endpoint인지
- source/rehearsal application integrity가 정확히 같은지
- revision 파일이 검토된 최초 revision 1개뿐인지

정상 결과:

```txt
classification: alembic-managed-baseline-complete
result: postgres-baseline-completion-state-verified
next safe stage: separate-read-only-next-revision-preflight
```

## 완료 상태의 의미

이제 원본 DB는 더 이상 `existing-schema-without-alembic-baseline`이 아닙니다.

과거 분류:

```txt
existing-schema-without-alembic-baseline
```

현재 분류:

```txt
alembic-managed-baseline-complete
```

기존 `stamp head`는 완료됐으므로 다시 실행하지 않습니다.

## 아직 승인되지 않은 것

v305 완료 상태는 다음 migration 실행 승인이 아닙니다.

```txt
새 Alembic revision 생성
autogenerate
upgrade
downgrade
stamp 재실행
DB create/drop/restore
.env/seed/auth/API write 변경
```

다음 단계는 먼저 **다음 revision 필요 여부와 변경 범위를 읽기 전용으로 확인하는 별도 preflight**입니다.

## 로컬 증거 보존

다음 증거는 사용자 PC에만 보존하며 Git/전달 ZIP/채팅에 포함하지 않습니다.

```txt
local-backups/
local-review-artifacts/alembic/v295_initial_schema.upgrade-v298.json
local-review-artifacts/alembic/v295_initial_schema.downgrade-v299.json
local-review-artifacts/alembic/v295_initial_schema.roundtrip-upgrade-v300.json
local-review-artifacts/alembic/v295_initial_schema.restore-rehearsal-stamp-v302.json
local-review-artifacts/alembic/v295_initial_schema.source-stamp-v304.json
```
