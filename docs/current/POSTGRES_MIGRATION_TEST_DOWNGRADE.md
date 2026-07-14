# PostgreSQL isolated migration test DB downgrade — v299

## 승인된 대상

```txt
rpg_game_migration_empty_v290
```

## 시작 상태

```txt
revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
public tables: 23
model tables: 22
alembic_version rows: 1
schema: structurally-equivalent
differences: 0
model table rows: 모두 0
```

v298 upgrade 검증 보고서도 다음 위치에서 확인합니다.

```txt
local-review-artifacts/alembic/v295_initial_schema.upgrade-v298.json
```

## 허용 명령

```txt
python -m alembic --config alembic.ini downgrade base
```

자식 프로세스의 `DATABASE_URL`만 `rpg_game_migration_empty_v290`으로 override합니다. `backend/.env`는 수정하지 않습니다.

## 실행 전 gate

- exact revision 파일과 SHA-256 일치
- 수동 검토 결과 일치
- v298 upgrade report 결과 일치
- target current revision이 정확히 `v295_initial_schema`
- target schema differences=0
- source `rpg_game`: 22 tables / 748 rows 유지
- rehearsal DB: 22 tables / 748 rows / differences=0 유지

## 성공 조건

```txt
public tables: ['alembic_version']
application tables remaining: 0
alembic_version rows: 0
current revisions: []
total rows: 0
schema classification: review-required
differences: 22
source/rehearsal: 작업 전후 동일
```

`differences=22`는 오류가 아니라, base 상태에서 모델 테이블 22개가 아직 없다는 뜻입니다.

## 생성되는 로컬 보고서

```txt
local-review-artifacts/alembic/v295_initial_schema.downgrade-v299.json
```

이 파일은 Git/전달 ZIP/채팅에서 제외합니다.

## 아직 금지

```txt
source DB upgrade/stamp
migration DB 자동 재-upgrade
createdb/dropdb
pg_restore
.env/Docker volume 변경
seed/인증/API write 변경
```
