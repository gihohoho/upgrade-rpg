# PostgreSQL backup/restore preflight — v290

현재 `rpg_game`은 22개 테이블과 748개 row가 있는 기존 데이터 보존 대상입니다.
v290은 실제 backup/restore를 실행하는 단계가 아니라, **실행 전 안전 경계와 도구 사용 가능 여부를 읽기 전용으로 확정하는 단계**입니다.

아래 작업은 아직 실행하지 않았습니다.

- backup 파일 생성
- restore
- 새 DB 생성/삭제
- Docker container/volume 변경
- `.env` 변경
- Alembic revision/upgrade/downgrade/stamp

## v290 읽기 전용 도구

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_backup_restore_preflight.py
```

JSON 결과가 필요할 때:

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_backup_restore_preflight.py --json
```

이 도구는 내부에서 v289 schema equivalence checker를 다시 실행하고 다음을 확인합니다.

1. 결과가 `structurally-equivalent`인지
2. `differenceCount`가 정확히 `0`인지
3. host 또는 실행 중인 PostgreSQL container에서 `pg_dump`, `pg_restore`, `createdb`, `dropdb`가 모두 사용 가능한지
4. backup 폴더가 Git 제외 규칙으로 보호되는지
5. source/restore rehearsal/migration test DB 이름이 서로 완전히 다른지

`review-required`, `connection-failed`, 도구 누락 중 하나라도 있으면 결과는 `blocked`이며 실제 backup 단계로 넘어가지 않습니다.

## 도구 점검 방식

먼저 host의 PostgreSQL client 도구를 확인합니다.

```txt
pg_dump --version
pg_restore --version
createdb --version
dropdb --version
```

host에 도구가 없어도 바로 설치할 필요는 없습니다.
기존 `upgrade_rpg_postgres` container가 실행 중이고 container 내부 네 도구가 모두 확인되면 `docker-container` 방식이 우선 선택됩니다.

container 확인은 아래와 같은 **버전 조회만** 수행합니다.

```txt
docker inspect --format {{.State.Running}} upgrade_rpg_postgres
docker exec upgrade_rpg_postgres pg_dump --version
docker exec upgrade_rpg_postgres pg_restore --version
docker exec upgrade_rpg_postgres createdb --version
docker exec upgrade_rpg_postgres dropdb --version
```

이 단계에서는 `pg_dump`, `pg_restore`, `createdb`, `dropdb`의 실제 동작 명령을 실행하지 않습니다.

## backup 저장 위치와 파일명 규칙

호스트 프로젝트 루트 기준:

```txt
local-backups/postgres/
```

파일명 규칙:

```txt
rpg_game_YYYYMMDD_HHMMSS_KST_v290.custom.dump
rpg_game_YYYYMMDD_HHMMSS_KST_v290.custom.dump.sha256
```

예시 형식만 보여주면 다음과 같습니다.

```txt
rpg_game_20260714_093000_KST_v290.custom.dump
```

실제 파일은 아직 만들지 않았습니다.

### format

- PostgreSQL custom format
- 향후 승인된 명령에서 `pg_dump -Fc` 사용
- plain SQL보다 `pg_restore`로 검증·복원 범위를 제어하기 쉬운 형식

### 민감정보 보존 규칙

backup에는 다음 데이터가 포함될 수 있습니다.

- 사용자 데이터
- 캐릭터/프로필 데이터
- 세이브 snapshot
- 관리자 변경 이력
- 기타 게임 운영 데이터

따라서 아래 규칙을 고정합니다.

- 외부 공유 금지
- Git commit 금지
- 전달 ZIP 포함 금지
- 메신저/클라우드에 무단 업로드 금지
- `.env` 자체는 dump에 포함되지 않음
- DB 접속 비밀번호를 파일명, 문서, 콘솔 출력에 넣지 않음
- backup 생성 후 SHA-256 sidecar로 파일 무결성 확인
- baseline 완료와 복원 성공 확인 전까지 최소 2개 세대 보존 권장

`.gitignore`에는 `/local-backups/`가 등록되어 있습니다.
전달 ZIP 생성 시에도 이 폴더를 명시적으로 제외합니다.

## DB 경계

### 원본 DB

```txt
rpg_game
```

- 보존 대상
- restore 대상이 될 수 없음
- rehearsal 중 schema/data write 금지
- backup 시 읽기만 허용

### restore rehearsal DB

```txt
rpg_game_restore_rehearsal_v290
```

- 원본과 완전히 다른 DB
- backup 복원 검증 전용
- 최초 생성/복원/삭제는 사용자 승인 후 각각 따로 실행
- 원본 DB 이름을 restore 대상에 넣는 명령은 금지

### 최초 migration test DB

```txt
rpg_game_migration_empty_v290
```

- restore rehearsal DB와도 다른 별도 빈 DB
- 향후 최초 Alembic revision을 검증하는 용도
- v290에서는 생성하지 않음
- revision/upgrade/downgrade/stamp 모두 실행하지 않음

세 DB 이름은 반드시 서로 달라야 합니다.

## restore 전후 비교 계획

### backup 전 원본 기록

1. current database/user/schema/PostgreSQL version
2. `public` table 수
3. 각 table의 row 수
4. 전체 row 합계
5. `alembic_version` 존재 여부
6. 보존 핵심 table row 수

현재 알려진 기준:

```txt
model tables: 22
public tables: 22
total rows: 748
alembic_version: 없음
users: 1
user_profiles: 1
characters: 1
user_save_snapshots: 2
admin_change_logs: 13
```

### restore 후 rehearsal DB 기록

1. 현재 연결된 DB가 `rpg_game_restore_rehearsal_v290`인지 확인
2. `public` table 수 비교
3. 모든 table의 row 수 일대일 비교
4. 전체 row 합계 비교
5. PK/FK/unique/index/check/type/nullability 비교
6. 원본과 rehearsal DB가 서로 다른 DB인지 다시 확인
7. FastAPI `.env`는 변경하지 않음

### 통과 조건

- 원본과 restore rehearsal DB의 table 목록 동일
- 22개 public table 유지
- 전체 748 row 유지
- table별 row count 모두 동일
- schema equivalence 차이 0개
- 원본 `rpg_game`의 schema/data 변화 0개

## 별도 빈 DB 최초 Alembic migration 검증 계획

실제 revision 생성 전에는 아래 순서만 계획으로 고정합니다.

1. backup/restore rehearsal 성공
2. `rpg_game_migration_empty_v290`가 비어 있음을 확인
3. 최초 revision 생성 명령은 사용자 별도 승인 후 실행
4. 생성된 revision 파일 전체 수동 검토
5. 빈 migration test DB에만 upgrade
6. model/schema 구조 비교
7. downgrade 가능성 검토 및 별도 승인
8. upgrade/downgrade 왕복 후 다시 구조 비교
9. 원본 DB에는 아직 upgrade/stamp하지 않음
10. 마지막에 기존 DB baseline stamp 여부를 별도 승인

## v290에서 확정한 실행 순서

1. 사용자 PC에서 schema checker 실제 결과 확인
2. 차이 0개일 때 preflight 도구 실행
3. `ready-for-user-approval` 결과와 도구 실행 mode 확인
4. 사용자에게 **backup 생성 한 단계만** 승인 요청
5. 승인 후 backup 생성
6. checksum과 파일 존재 확인
7. 그 다음 별도 DB 생성 승인을 다시 요청
8. restore 승인을 다시 요청
9. 비교 완료 후 rehearsal DB 삭제 승인을 다시 요청

한 번의 승인으로 backup/restore/DB 생성·삭제를 묶지 않습니다.

## 계속 실행 금지

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
pg_dump 실제 backup 명령
createdb 실제 DB 생성 명령
pg_restore 실제 restore 명령
dropdb 실제 DB 삭제 명령
```

위 항목은 각각 사용자 명시 승인 전까지 실행하지 않습니다.

## v292 빈 restore rehearsal DB 경계

- source: `rpg_game`
- target: `rpg_game_restore_rehearsal_v290`
- target 존재 시 즉시 중단
- 없을 때만 owner `rpg_user`, template `template0`으로 생성
- 생성 후 public tables 0, `alembic_version` 없음 확인
- restore/drop/Alembic은 별도 승인 전 금지


## v293 verified restore 실행 경계

- source: `rpg_game` read-only
- target: `rpg_game_restore_rehearsal_v290` write-only
- exact dump/SHA/source snapshot 재검증
- target 0 tables/0 rows gate
- `pg_restore --single-transaction --exit-on-error --no-owner --no-privileges`
- restore 후 target 22 tables / 748 rows / table별 counts / schema differences=0
- source 작업 전후 동일
- no create/clean/drop/Alembic mutation
