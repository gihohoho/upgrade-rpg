# Seed Import 긴 이미지/아이콘 URL 수정

## 문제

`python scripts/setup_dev_db.py --reset --seed --verify` 실행 중 아래 오류가 날 수 있었습니다.

```txt
psycopg.errors.StringDataRightTruncation: value too long for type character varying(500)
```

원인은 `item_templates.icon_url`에 들어가는 SVG `data:image` 문자열이 500자를 넘는 경우가 있기 때문입니다.
기존 DB 초안은 이미지/아이콘 URL을 일반 URL 정도로 보고 `VARCHAR(500)`으로 잡았지만, 현재 게임 seed에는 SVG data URL이 포함됩니다.

## 수정

아래 컬럼을 `TEXT` 타입으로 변경했습니다.

- `characters.image_url`
- `skills.icon_url`
- `item_templates.icon_url`
- `bosses.image_url`

로컬 개발 DB에서는 `--reset`을 다시 실행하면 새 타입으로 테이블이 생성됩니다.

## 다시 실행

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
source .venv/Scripts/activate
python scripts/setup_dev_db.py --reset --seed --verify
```

정상이면 `item_templates`가 245개로 들어가야 합니다.

## SQL 로그

긴 SVG data URL 때문에 seed import SQL 로그가 너무 길어지는 문제가 있어, `setup_dev_db.py`는 기본적으로 SQL 원문을 출력하지 않습니다.

정말 SQL 로그가 필요할 때만 아래처럼 실행합니다.

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/setup_dev_db.py --reset --seed --verify --verbose-sql
```
