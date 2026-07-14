# PostgreSQL restore rehearsal database creation — v292

## 목적

v292는 검증된 v291 backup을 실제 원본 DB와 완전히 분리된 빈 PostgreSQL DB에 복원하기 전, **빈 리허설 DB 하나만 안전하게 만드는 단계**입니다.

승인된 target DB:

```txt
rpg_game_restore_rehearsal_v290
```

원본 DB:

```txt
rpg_game
```

원본 DB와 target DB 이름은 고정되어 있으며 서로 바꿀 수 없습니다.

## 사용자 PC에서 이미 확인된 backup

```txt
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
size: 126.60 KB
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
source tables: 22
source total rows: 748
TOC table definitions/data entries: 22 / 22
```

backup과 `local-backups/` 폴더는 민감정보 보존 대상이므로 Git, 전달 ZIP, 채팅에 포함하지 않습니다.

## 실행 도구

```txt
tools/create_postgres_restore_rehearsal_database.py
```

이 도구는 다음 순서로 실행됩니다.

1. schema equivalence와 backup/restore preflight gate 재확인
2. 원본 `rpg_game`이 22 tables / 748 rows / Alembic 이력 없음인지 확인
3. 사용자가 승인한 정확한 backup filename/manifest와 실제 dump의 SHA-256 재계산·비교
4. PostgreSQL catalog에서 target DB 존재 여부 확인
5. target이 이미 있으면 즉시 중단
6. 없을 때만 `createdb`로 정확히 한 번 생성
7. source와 같은 encoding/collation/locale provider 사용
8. owner `rpg_user`, template `template0` 고정
9. target public table 0개와 `alembic_version` 없음 확인
10. 원본 DB가 여전히 22 tables / 748 rows인지 다시 확인

## 실행 명령

먼저 가상환경 활성화:

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/create_postgres_restore_rehearsal_database.py --execute
```

## 성공 기준

```txt
result: restore-rehearsal-database-created-empty-and-verified
target DB: rpg_game_restore_rehearsal_v290
target public tables: 0
target alembic_version: absent
source tables before/after: 22 / 22
source rows before/after: 748 / 748
```

## 이번 단계에서 실행하지 않는 것

- `pg_restore`
- target DB table/data 생성
- `dropdb`
- 원본 DB schema/data 변경
- `.env` 변경
- Docker container/volume 변경
- Alembic revision/upgrade/downgrade/stamp
- API/auth/write/game content 변경

## 실패 시 원칙

- target DB가 이미 있으면 생성·복원·삭제 모두 중단합니다.
- 생성 후 검증이 예상과 다르면 자동 `dropdb`를 하지 않습니다.
- 오류 결과를 먼저 분석한 뒤 별도 승인 범위를 정합니다.

## 다음 승인 경계

빈 target DB 생성과 검증이 성공한 뒤에만, verified dump를 `pg_restore`로 target에 쓰는 작업을 별도로 승인받습니다.
