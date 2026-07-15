# NEXT CHAT HANDOFF — Upgrade RPG v306

## 기준 ZIP

- `rpg_v306_postgres_next_revision_readonly_preflight_ready.zip`

## 현재 버전

- 최신 작업: `v306.postgres-next-revision-readonly-preflight`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 DB 상태

```txt
source rpg_game:
  public tables/rows 23/749
  application tables/rows 22/748
  current revision v295_initial_schema
  runtime classification alembic-managed
  v304 execution report verified

restore rehearsal rpg_game_restore_rehearsal_v290:
  public tables/rows 23/749
  application tables/rows 22/748
  current revision v295_initial_schema
  v302 execution report verified

migration rpg_game_migration_empty_v290:
  public tables/rows 23/1
  current revision v295_initial_schema
  differences=0
```

프로젝트 분류:

```txt
alembic-managed-baseline-complete
```

## 고정 증거

```txt
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
backup SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
```

로컬 backup과 review evidence는 Git/ZIP/채팅에 포함하지 않습니다.

## 사용자 PC에서 실제 완료

```txt
v298 first upgrade: passed
v299 downgrade base: passed
v300 second upgrade: passed
first/second upgrade signatures: identical
v301 source preflight: passed
v302 rehearsal stamp: passed
v303 rehearsal post-check: restore-rehearsal-stamp-current-state-verified
v304 source stamp/post-check: source-baseline-stamp-current-state-verified
v305 completion check: postgres-baseline-completion-state-verified
```

## v306 추가 내용

```txt
tools/check_postgres_next_revision_preflight.py
tools/smoke/backend/smoke_postgres_next_revision_preflight.py
docs/current/POSTGRES_NEXT_REVISION_PREFLIGHT.md
docs/current/POSTGRES_NEXT_REVISION_READONLY_PLAN.md
```

v306 preflight는 다음을 읽기 전용으로 확인합니다.

- v305 baseline completion 유지
- Alembic graph single base/single head
- exact reviewed revision file 1개
- 승인 SQLAlchemy model/Alembic env source snapshot 13개
- canonical schema 22/22, differences=0
- PostgreSQL read-only transaction + SQL write guard
- Alembic metadata candidate operation
- type/server default/nullable/index/constraint 비교
- integer PK sequence ownership과 unowned sequence

## 다음 첫 작업

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_next_revision_preflight.py --strict
```

변경 없음 정상 기대 핵심:

```txt
baseline completion: postgres-baseline-completion-state-verified
Alembic graph heads/bases: ['v295_initial_schema']/['v295_initial_schema']
approved model source snapshot: matched / 13 files
SQLAlchemy metadata tables: 22
canonical schema: structurally-equivalent / differences=0
Alembic candidate operations: 0
next revision required: no
result: next-revision-not-required-current-schema-equivalent
next safe stage: keep-single-baseline-no-new-revision
```

후보가 발견되면 `next-revision-review-required-schema-differences-detected`로 중지하고 autogenerate를 실행하지 않습니다.

## 다음 안전 순서

1. v306 실제 결과 확인
2. candidate operation 0개면 새 revision 생성 보류
3. 후보가 있으면 schema change intent와 748개 row 영향 검토
4. autogenerate는 별도 사용자 승인 전 금지
5. 향후 revision은 isolated migration DB에서 먼저 검토·왕복
6. source 적용은 다시 별도 승인

## 절대 변경/실행 금지

- source/rehearsal `stamp` 재실행
- 새 Alembic revision 생성/autogenerate
- source/rehearsal/migration `upgrade`/`downgrade`
- DB 생성/삭제/복원
- Docker container/volume 삭제
- `.env`, seed, 인증
- 기존 API route path/response body
- 실제 write 로직/Write Guard
- Preview/Apply request body
- 게임 콘텐츠/밸런스 변경
