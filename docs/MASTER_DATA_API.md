# Master Data API

`v081`부터 `/api/v1/game/master-data`는 더 이상 임시 `stub` 응답만 반환하지 않습니다.
로컬 PostgreSQL에 import된 seed 테이블을 읽어서 프론트엔드가 사용할 수 있는 마스터 데이터를 내려줍니다.

## 실행 전 조건

아래 작업이 먼저 완료되어 있어야 합니다.

1. Docker PostgreSQL 실행
2. seed JSON 생성
3. seed 데이터를 PostgreSQL에 import
4. FastAPI 서버 실행

## seed import

위치: **프로젝트 루트**

```bash
node tools/extract_seed_data.js
node tools/smoke_seed_extraction.js
```

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
source .venv/Scripts/activate
python scripts/setup_dev_db.py --reset --seed --verify
```

## 서버 실행

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
uvicorn app.main:app --reload
```

브라우저 확인:

```txt
http://127.0.0.1:8000/api/v1/game/master-data
```

## 터미널 확인 스크립트

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/check_master_data_api.py
```

정상이면 아래처럼 출력됩니다.

```txt
master-data API check passed
```

## 응답 구조

응답은 기존 `game-api-response.v1` 계약을 유지합니다.

```json
{
  "ok": true,
  "responseVersion": "game-api-response.v1",
  "type": "game.master_data",
  "payload": {
    "characters": [],
    "skills": [],
    "characterSkills": [],
    "skillLevels": [],
    "itemTemplates": [],
    "bosses": [],
    "fieldZones": [],
    "dropTables": [],
    "dropTableItems": [],
    "enhancementGroups": [],
    "enhancementLevels": [],
    "enhancementRules": {
      "groups": [],
      "levels": []
    },
    "counts": {}
  },
  "data": {
    "status": "loaded",
    "userId": 1
  },
  "meta": {
    "source": "postgresql",
    "counts": {}
  },
  "error": null
}
```

## 현재 포함되는 데이터

- characters
- skills
- characterSkills
- skillLevels
- itemTemplates
- bosses
- fieldZones
- dropTables
- dropTableItems
- enhancementGroups
- enhancementLevels
- enhancementRules

## 다음 단계

다음 단계에서는 프론트엔드가 아직 JS 파일에서 직접 읽는 마스터 데이터를 FastAPI API 응답으로 점진적으로 교체할 준비를 합니다.
단, 게임 화면 전체를 한 번에 API로 바꾸기보다는 먼저 읽기 전용 브릿지부터 붙이는 방식이 안전합니다.

## seed import가 0개로 보일 때

`scripts/check_master_data_api.py`에서 모든 개수가 0으로 나오면 API가 실패한 것이 아니라 seed import가 중간에 실패해 롤백됐을 수 있습니다.

특히 아래 오류가 있으면 이미지/아이콘 URL 컬럼 길이 문제입니다. v082 이상에서는 해당 컬럼을 `TEXT`로 변경했습니다.

```txt
value too long for type character varying(500)
```

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/setup_dev_db.py --reset --seed --verify
```
