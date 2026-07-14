# PostgreSQL backup creation and verification — v291

## 목적

사용자 승인 범위: 원본 `rpg_game`의 실제 backup 생성 한 단계만 허용합니다.

v291은 v290 preflight에서 승인된 범위에 따라 **원본 `rpg_game`을 읽어 로컬 backup 파일을 만드는 작업만** 수행합니다.

실행 도구:

```txt
tools/create_postgres_backup.py
```

이 도구는 다음을 실행하지 않습니다.

- restore
- `createdb`
- `dropdb`
- Docker container/volume 생성·삭제·재시작
- `.env` 변경
- Alembic revision/upgrade/downgrade/stamp
- 원본 DB schema/data write

## 실행 전 확인

도구는 사용자가 별도로 preflight를 다시 실행하지 않아도 내부에서 아래 gate를 즉시 재검사합니다.

1. schema classification이 `structurally-equivalent`
2. difference count가 `0`
3. preflight가 `ready-for-user-approval`
4. selected mode가 `docker-container`
5. `upgrade_rpg_postgres` container가 실행 중
6. 실제 연결 DB가 정확히 `rpg_game`
7. 실제 DB user가 정확히 `rpg_user`
8. model/public table 경계가 동일
9. table별 row count 수집 성공

하나라도 다르면 backup 파일을 만들지 않습니다.

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
python tools/create_postgres_backup.py --execute
```

`--execute`가 없으면 실제 파일을 만들지 않고 실행 계획만 출력한 뒤 중단합니다.

## 생성되는 파일

폴더:

```txt
local-backups/postgres/
```

한 번 실행하면 같은 timestamp를 공유하는 아래 파일들이 생성됩니다.

```txt
rpg_game_YYYYMMDD_HHMMSS_KST_v290.custom.dump
rpg_game_YYYYMMDD_HHMMSS_KST_v290.custom.dump.sha256
rpg_game_YYYYMMDD_HHMMSS_KST_v290.custom.dump.toc.txt
rpg_game_YYYYMMDD_HHMMSS_KST_v290.custom.dump.source.json
rpg_game_YYYYMMDD_HHMMSS_KST_v290.custom.dump.manifest.json
```

`v290` 표시는 v290에서 승인된 backup 파일 정책을 그대로 실행한다는 뜻입니다.
프로젝트 코드/ZIP 버전은 v291입니다.

## 생성 순서와 안전장치

1. source 상태와 row count를 읽기 전용으로 기록
2. `.partial` 파일을 새로 생성하며 기존 파일 덮어쓰기 거부
3. container 내부 `pg_dump 16.14`를 custom format으로 실행
4. binary stdout을 shell redirection 없이 Python이 직접 파일에 기록
5. `pg_restore --list`로 archive TOC 읽기 검증
6. 원본 public table마다 `TABLE`과 `TABLE DATA` entry 확인
7. 검증 성공 후에만 `.partial`을 정식 `.dump`로 rename
8. SHA-256 계산
9. TOC/source snapshot/manifest 작성

검증 실패 시 정식 `.dump` 파일을 게시하지 않고 `.partial` 파일을 제거합니다.

## 정상 결과 기준

콘솔에서 다음 항목을 확인합니다.

```txt
result: backup-created-and-verified
backup: local-backups/postgres/...
size: 0보다 큰 값
SHA-256: 64자리 해시
source tables: 22
source total rows: 현재 실제 값
toc format: CUSTOM
TOC table definitions verified: 22
TOC table data entries verified: 22
```

현재 알려진 row 기준은 748이지만 실제 실행 시점에 사용자 데이터가 합법적으로 바뀌었다면 도구가 그 시점의 값을 snapshot에 기록합니다.

## 민감정보 규칙

`.dump`에는 사용자, 캐릭터, 프로필, 세이브 snapshot, 관리자 변경 이력 등 실제 데이터가 포함될 수 있습니다.

- `.dump` 파일 업로드 금지
- Git commit 금지
- 전달 ZIP 포함 금지
- 외부 메신저/클라우드 공유 금지
- 콘솔 결과만 다음 채팅에 전달
- `.env`와 비밀번호는 dump/manifest에 넣지 않음
- checksum은 무결성 확인용이며 비밀번호가 아님

`/local-backups/`는 `.gitignore`와 `.dockerignore`에 등록되어 있습니다.

## 다음 단계

backup 성공 후에도 자동으로 다음 작업을 실행하지 않습니다.

다음 별도 승인 후보는 **빈 restore rehearsal DB 생성 한 단계**입니다.

```txt
rpg_game_restore_rehearsal_v290
```

그 이후 restore, 원본/복원 비교, rehearsal DB 삭제도 각각 별도로 승인합니다.

## 사용자 PC 실제 결과

```txt
result: backup-created-and-verified
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
size: 126.60 KB
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
source tables/rows: 22 / 748
TOC definitions/data: 22 / 22
```

다음 단계는 `tools/create_postgres_restore_rehearsal_database.py --execute`로 빈 target DB만 생성하는 v292 경계입니다.
