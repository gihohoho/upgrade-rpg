# Neon database initialization and migration plan — v345

## 결론

새 `rpg_game` DB를 만들지 않고 restore 전에는 비어 있던 production branch의 `neondb`를 사용합니다. 앱은 DB 이름을 코드에 고정하지 않고 `DATABASE_URL`을 사용하므로 DB 생성 단계를 없애는 편이 단순하고 안전합니다.

2026-07-26 restore와 exact stamp 후 최종 read-only 확인 결과:

```txt
database/role: neondb / neondb_owner
public base tables: 23
application rows: 748
total rows: 749
alembic_version: v295_initial_schema / 1 row
TLS hostname verification: 통과
read-only inspection write: 없음
```

정적 계약은 `deploy/neon-database-initialization-migration.example.json`입니다. 실제 endpoint, password, URL은 기록하지 않습니다.

## 선택한 이식 방식

검증된 local custom dump를 Neon direct URL로 복원한 뒤 exact `v295_initial_schema`를 stamp합니다.

```txt
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
backup application tables/rows: 22 / 748
backup alembic_version: 없음
reviewed revision: v295_initial_schema
```

빈 DB에 `alembic upgrade head`만 실행하는 방식은 schema만 만들고 748행을 옮기지 못합니다. seed JSON은 아직 자동 import 도구가 아니므로 현재 이식 경로로 사용하지 않습니다.

## 연결 정책

- `pg_restore`와 Alembic은 Neon **direct URL만** 사용합니다.
- 앱과 Alembic은 Windows 시스템 CA를 사용하는 hostname-verifying SSLContext로 검증합니다.
- 이 PC의 PostgreSQL 16/OpenSSL은 `sslrootcert=system`에서 `unregistered scheme` 오류가 발생하므로, 공개 Windows 시스템 CA를 Git 제외 로컬 PEM으로 내보내 `pg_restore`/`psql`의 `verify-full`에 전달합니다.
- pooled URL은 restore/Alembic에 사용하지 않습니다.
- 앱 runtime도 단일 worker와 기존 SQLAlchemy pool을 고려해 direct URL을 사용합니다.
- 실제 URL은 `deploy/.env.production`과 Render secret store 밖으로 출력하지 않습니다.

## v343 실행 결과와 안전 중단

승인된 preparation SHA `d6df9984e00d08b28fd524dcfefeb492e334d5e9`로 `pg_restore`를 한 번 실행했습니다. 단일 트랜잭션 restore가 완료된 뒤 22 application tables, 748 rows, schema digest가 일치했습니다.

기존 data digest는 timezone-aware datetime을 현재 DB session offset 문자열로 해시했습니다. verified rehearsal은 `Asia/Seoul`, Neon은 `GMT`여서 같은 시각도 다른 문자열이 되었고 도구는 Alembic stamp 전에 안전하게 중단했습니다. 양쪽 44개 `timestamptz` 컬럼을 UTC로 정규화해 다시 계산한 application data digest는 아래와 같이 정확히 일치합니다.

```txt
schema: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data:   4ea23cfd2446b522cc9e85e2a8520160427cf8e3987d9b6ab04f4b99fbf6c00c
alembic_version: 없음
```

sanitized evidence는 `deploy/review/neon-restore-prestamp-verification-v344.json`입니다. 복원은 재실행하지 않습니다.

## v344에서 사용한 stamp recovery 승인 경계

`tools/initialize_neon_database.py`가 아래 조건을 모두 fail-closed로 확인합니다.

- 실행 commit이 clean `main` HEAD이며 pushed `origin/main`과 같음
- 사용자가 승인한 정확한 40자리 preparation SHA와 현재 HEAD가 같음
- target `neondb`, backup SHA-256, revision `v295_initial_schema`, action `verify-restored-and-stamp-once`가 모두 정확함
- Neon direct target이 실행 직전에도 22 application tables / 748 rows / UTC-normalized digest 일치 / no Alembic임
- pooled URL, `--create`, `--clean`, upgrade/downgrade, 자동 retry/cleanup은 사용하지 않음
- 이미 완료된 `pg_restore` 재실행은 거부함

v344 당시 기본 실행과 focused smoke는 DB에 연결하지 않았고 `--inspect`만 read-only transaction과 libpq `verify-full` preflight를 수행했습니다. 과거 `--execute`는 복원 완료 뒤 비활성화됐고, 승인된 `--resume-stamp`만 exact recovery 조건에서 한 번 열렸습니다.

## v344 exact-SHA 승인으로 실행한 recovery 순서

1. 새 recovery preparation SHA가 clean pushed `main` HEAD와 같은지 확인
2. target, backup SHA-256, revision, `verify-restored-and-stamp-once` confirmation 확인
3. application 22 tables / 748 rows / UTC-normalized schema·data digest 일치와 no Alembic 재확인
4. `pg_restore`는 실행하지 않음
5. exact revision `v295_initial_schema`만 stamp
6. public 23 tables / 749 rows, application digest 불변, current v295 확인

stamp recovery는 Render 배포 승인과 다른 **DB stamp recovery 전용 준비 commit의 exact SHA 승인**을 받아야 합니다. 자동 retry, 자동 cleanup, reset, truncate, seed, upgrade/downgrade는 포함하지 않습니다.

## v345 완료 상태

승인된 recovery SHA `cf0f506b6ae9dc9d4c02f3ab5313ca68be32676c`로 위 순서를 한 번 실행했습니다. `pg_restore`는 재실행하지 않았고 exact `v295_initial_schema` stamp와 최종 23 tables / 749 rows 검증이 통과했습니다. application schema/data digest는 stamp 전후 불변입니다.

현재 `tools/initialize_neon_database.py`의 `--execute`와 `--resume-stamp`는 모두 비활성화됐습니다. 기본 모드는 static 완료 상태만 확인하고 `--inspect`만 23/749, exact v295, TLS를 read-only로 재검증합니다. 최종 sanitized evidence는 `deploy/review/neon-initialization-completed-v345.json`입니다.

## 실패 시 중단

- restore 실패: single transaction 결과를 read-only 확인하고 자동 재시도·정리하지 않음
- 복원 후 검증 실패: target을 보존하고 stamp·Render 진행 중단
- stamp 실패: 복원 데이터를 보존하고 Render 진행 중단
- 어떤 실패에서도 DB drop/create/reset 또는 `--clean`을 자동 실행하지 않음

## Render보다 먼저 하는 이유

Render Free는 pre-deploy command와 Shell/one-off job을 지원하지 않습니다. 앱 image도 시작 시 migration을 실행하지 않습니다. 그러므로 Neon 초기화를 먼저 끝내지 않으면 첫 Render deploy가 빈 DB에 연결되거나 실패할 수 있습니다.

v341 source의 Neon verify-full SQLAlchemy bootstrap은 실제 Neon direct read-only 연결까지 통과했고, 새 exact image의 게시와 isolated CA-store/runtime 검증도 완료했습니다. 최종 순서는 다음과 같습니다.

```txt
bootstrap fix → new image publish/isolated validation 완료
→ 별도 exact-SHA 승인 뒤 Neon restore 1회 완료
→ 새 exact-SHA 승인 뒤 restored-state verification + exact v295 stamp
→ Render service create/deploy
```

## 공식 근거

- Neon 기본 `neondb`와 database 관리: https://neon.com/docs/manage/databases
- `pg_dump`/`pg_restore`는 direct 연결 사용: https://neon.com/docs/import/migrate-from-neon
- migration에는 direct 연결 권장: https://neon.com/docs/connect/connection-pooling
- `verify-full`과 PostgreSQL 16 시스템 CA: https://neon.com/blog/avoid-mitm-attacks-with-psql-postgres-16
- SQLAlchemy asyncpg와 PgBouncer 주의: https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#asyncpg
