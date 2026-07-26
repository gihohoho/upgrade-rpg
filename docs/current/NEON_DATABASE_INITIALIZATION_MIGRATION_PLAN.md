# Neon database initialization and migration plan — v343

## 결론

새 `rpg_game` DB를 만들지 않고 기존 production branch의 빈 `neondb`를 사용합니다. 앱은 DB 이름을 코드에 고정하지 않고 `DATABASE_URL`을 사용하므로 DB 생성 단계를 없애는 편이 단순하고 안전합니다.

2026-07-26 read-only 확인 결과:

```txt
database/role: neondb / neondb_owner
public base tables: 0
alembic_version: 없음
TLS hostname verification: 통과
database write: 없음
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

## 준비된 실행 도구와 승인 경계

`tools/initialize_neon_database.py`가 아래 조건을 모두 fail-closed로 확인합니다.

- 실행 commit이 clean `main` HEAD이며 pushed `origin/main`과 같음
- 사용자가 승인한 정확한 40자리 preparation SHA와 현재 HEAD가 같음
- target `neondb`, backup SHA-256, revision `v295_initial_schema`, action `restore-and-stamp-once`가 모두 정확함
- Neon direct target이 실행 직전에도 0 table / no Alembic임
- pooled URL, `--create`, `--clean`, upgrade/downgrade, 자동 retry/cleanup은 사용하지 않음

기본 실행과 focused smoke는 DB에 연결하지 않습니다. `--inspect`만 read-only transaction과 libpq `verify-full` preflight를 수행합니다. `--execute`는 위 exact 승인 입력이 모두 맞아야만 열립니다.

## 별도 exact-SHA 승인 뒤 실행할 순서

1. Neon `neondb`가 0 table / no Alembic인지 read-only 재확인
2. backup filename, size, SHA-256, table 목록, 행 수 snapshot 재확인
3. direct URL과 verify-full을 고정한 `pg_restore` 실행
4. `--exit-on-error --single-transaction --no-owner --no-privileges` 사용
5. `--create`, `--clean`은 사용하지 않음
6. 복원 뒤 application 22 tables / 748 rows / schema·data digest 일치 확인
7. 아직 `alembic_version`이 없는지 확인
8. exact revision `v295_initial_schema`만 stamp
9. public 23 tables / 749 rows, application digest 불변, current v295 확인

restore와 stamp는 Render 배포 승인과 다른 **DB 초기화 전용 준비 commit의 exact SHA 승인**을 받아야 합니다. 자동 retry, 자동 cleanup, reset, truncate, seed, upgrade/downgrade는 포함하지 않습니다.

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
→ 별도 exact-SHA 승인 뒤 Neon restore/stamp/verification
→ Render service create/deploy
```

## 공식 근거

- Neon 기본 `neondb`와 database 관리: https://neon.com/docs/manage/databases
- `pg_dump`/`pg_restore`는 direct 연결 사용: https://neon.com/docs/import/migrate-from-neon
- migration에는 direct 연결 권장: https://neon.com/docs/connect/connection-pooling
- `verify-full`과 PostgreSQL 16 시스템 CA: https://neon.com/blog/avoid-mitm-attacks-with-psql-postgres-16
- SQLAlchemy asyncpg와 PgBouncer 주의: https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#asyncpg
