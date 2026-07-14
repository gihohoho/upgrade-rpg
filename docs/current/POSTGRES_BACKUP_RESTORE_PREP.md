# PostgreSQL backup/restore 준비 계획 — v289

현재 DB는 22개 테이블과 748개 row가 있는 기존 데이터 보존 대상입니다.
이 문서는 다음 단계에서 수행할 backup/restore 리허설의 범위만 고정합니다.
아직 backup, restore, 새 DB 생성, migration 생성, stamp를 실행하지 않습니다.

## 현재 확인된 대상

```txt
Docker Compose project: upgraderpg
PostgreSQL container: upgrade_rpg_postgres
volume: upgraderpg_rpg_postgres_data
source DB: rpg_game
source user: rpg_user
host port: 55432
```

## v290에서 준비할 것

1. backup 파일 저장 폴더와 파일명 규칙
2. backup 생성 전 DB identity/row count 기록
3. `pg_dump` 도구 사용 가능 여부 확인
4. 원본 DB와 분리된 restore rehearsal DB 이름 결정
5. restore 전후 테이블 수와 row count 비교 도구
6. restore rehearsal 정리 방법
7. 실패 시 원본 DB에 영향이 없다는 보장
8. 최초 Alembic revision을 별도 빈 DB에서 검증하는 순서

## 기본 보존 원칙

- 원본 `rpg_game` DB에는 restore하지 않습니다.
- Docker volume `upgraderpg_rpg_postgres_data`를 삭제하지 않습니다.
- `docker compose down -v`를 사용하지 않습니다.
- `setup_dev_db.py --reset`을 사용하지 않습니다.
- 실제 backup 파일은 Git과 전달 ZIP에 포함하지 않습니다.
- backup 파일에는 사용자/세이브 데이터가 포함되므로 외부 공유하지 않습니다.

## 사용자 승인 전 실행 금지

```txt
pg_dump ...
createdb ...
dropdb ...
pg_restore ...
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic stamp head
```

위 명령은 v290에서 명령·대상·복구 경계를 먼저 검토한 뒤 작은 단계로 진행합니다.
