# Seed Import Guide

이 문서는 현재 JS 마스터 데이터를 PostgreSQL 로컬 DB에 넣는 절차를 설명합니다.

## 목적

`tools/extract_seed_data.js`가 생성한 JSON 파일을 PostgreSQL 테이블에 넣어, 이후 FastAPI의 `/game/master-data` API와 관리자 페이지 개발에서 사용할 수 있게 합니다.

## 실행 전 준비

아래가 끝나 있어야 합니다.

- Docker Desktop 실행 중
- `docker compose up -d`로 `upgrade_rpg_postgres` 컨테이너 실행 중
- `backend/.env` 생성 완료
- FastAPI 패키지 설치 완료

## 명령어 위치 규칙

- JS seed 추출 도구는 **프로젝트 루트**에서 실행합니다.
- DB import 스크립트는 **backend 폴더**에서 실행합니다.

## 1. seed JSON 다시 생성

위치: **프로젝트 루트**

```bash
node tools/extract_seed_data.js
node tools/smoke_seed_extraction.js
```

생성 위치:

```txt
backend/seeds/generated/
```

## 2. import 전 dry-run 확인

위치: **backend 폴더**

```bash
python scripts/setup_dev_db.py --dry-run
```

이 명령은 DB에 접근하지 않고 seed JSON 개수만 확인합니다.

## 3. 로컬 DB 초기화 + 테이블 생성 + seed import

위치: **backend 폴더**

```bash
python scripts/setup_dev_db.py --reset --seed --verify
```

주의:

```txt
--reset은 로컬 PostgreSQL public schema를 삭제 후 다시 만듭니다.
개발용 DB에서만 사용하세요.
```

## 4. 기존 데이터를 유지하면서 테이블만 만들기

위치: **backend 폴더**

```bash
python scripts/setup_dev_db.py --create-schema
```

## 5. seed만 다시 넣기

위치: **backend 폴더**

```bash
python scripts/setup_dev_db.py --seed --verify
```

## 현재 import 대상

- characters
- skills
- character_skills
- skill_levels
- item_templates
- bosses
- field_zones
- drop_tables
- drop_table_items
- enhancement_groups
- enhancement_levels
- admin_roles

## 큰 숫자 처리

현재 게임은 HP/골드가 매우 큰 값까지 올라갑니다. 그래서 DB 초안의 HP/골드/강화비용 계열 컬럼은 `INTEGER`가 아니라 `NUMERIC(40,0)`을 사용하도록 보정했습니다.


## 연결 오류가 날 때

만약 `--reset --seed --verify` 실행 중 아래 오류가 나오면:

```txt
asyncpg.exceptions.ConnectionDoesNotExistError: connection was closed in the middle of operation
```

`v079`부터 seed import 스크립트는 동기식 `psycopg` 방식으로 변경되어 이 문제를 피하도록 되어 있습니다.

이미 가상환경을 만든 상태라면 먼저 아래를 설치하세요.

위치: **backend 폴더**

```bash
pip install "psycopg[binary]"
```

그 다음 다시 실행합니다.

위치: **backend 폴더**

```bash
python scripts/setup_dev_db.py --reset --seed --verify
```


## 긴 이미지/아이콘 URL 처리

현재 seed에는 SVG `data:image` URL이 들어갈 수 있습니다. 일반 URL보다 길기 때문에 이미지/아이콘 컬럼은 `VARCHAR(500)`이 아니라 `TEXT` 타입을 사용합니다.

관련 컬럼:

- `characters.image_url`
- `skills.icon_url`
- `item_templates.icon_url`
- `bosses.image_url`

만약 아래 오류가 나오면 v082 이상 ZIP을 적용한 뒤 `--reset --seed --verify`를 다시 실행하세요.

```txt
value too long for type character varying(500)
```

자세한 내용은 `docs/SEED_IMPORT_LONG_ASSET_FIX.md`를 참고하세요.

## 다음 단계

seed import가 성공하면 다음 단계는 `/game/master-data` API가 DB에서 실제 데이터를 읽어오게 만드는 작업입니다.


> 로컬 PostgreSQL은 기본 포트 `5432`가 아니라 `55432`를 사용한다. Windows에서 기존 PostgreSQL과 충돌을 피하기 위한 프로젝트 기준이다. 자세한 내용은 `docs/LOCAL_DB_PORT_POLICY.md`를 참고한다.
