# Master Data Parity Checker

## 목적

`v086`은 현재 JS 마스터 데이터에서 추출한 seed JSON과 FastAPI `/api/v1/game/master-data` 응답이 같은지 비교하는 검증 도구를 추가한다.

이 단계의 목표는 아직 게임 화면을 API 데이터로 교체하는 것이 아니다. 먼저 아래 흐름이 기존 JS 데이터와 같은 내용을 유지하는지 확인한다.

```txt
src/data/*.js
→ tools/extract_seed_data.js
→ backend/seeds/generated/*.json
→ PostgreSQL
→ FastAPI /api/v1/game/master-data
```

## 추가 파일

```txt
backend/scripts/check_master_data_parity.py
tools/smoke/game/smoke_master_data_parity_checker.py
docs/archive/stage-notes/MASTER_DATA_PARITY_CHECKER.md
```

## 실행 전 준비

1. seed JSON 생성

위치: 프로젝트 루트

```bash
node tools/extract_seed_data.js
```

2. seed DB import

위치: backend 폴더 + 가상환경 activate 상태

```bash
source .venv/Scripts/activate
python scripts/setup_dev_db.py --reset --seed --verify
```

3. FastAPI 실행

위치: backend 폴더 + 가상환경 activate 상태

```bash
uvicorn app.main:app --reload
```

## parity 검사 실행

새 터미널에서 실행한다.

위치: backend 폴더 + 가상환경 activate 상태

```bash
source .venv/Scripts/activate
python scripts/check_master_data_parity.py
```

정상이라면 다음 문구가 나온다.

```txt
master-data parity check passed
```

## 이미지 포함 응답까지 비교

기본 master-data 응답은 백신 오탐과 응답 크기 문제를 줄이기 위해 긴 `data:image/...` 문자열을 제외한다.

정확한 이미지 문자열까지 비교하려면 아래처럼 실행한다.

위치: backend 폴더 + 가상환경 activate 상태

```bash
python scripts/check_master_data_parity.py --include-assets
```

이 경우 API 요청은 다음 주소로 나간다.

```txt
http://127.0.0.1:8000/api/v1/game/master-data?includeAssets=true
```

## 비교 항목

현재 비교하는 주요 항목은 다음과 같다.

```txt
counts
characters
characterSkills
skills
skillLevels
itemTemplates
bosses
fieldZones
dropTables
dropTableItems
enhancementGroups
enhancementLevels
```

각 항목은 개수뿐 아니라 code/id, 이름, 타입, 주요 숫자 값, 드랍 테이블 연결 관계 등도 함께 비교한다.

## 실패했을 때 보는 법

실패하면 아래처럼 JSON 리포트가 출력된다.

```json
{
  "ok": false,
  "failures": []
}
```

`failures` 안의 `area`를 보면 어느 영역에서 차이가 났는지 알 수 있다.

예시:

```txt
area: itemTemplates      아이템 템플릿 차이
area: bosses             보스 데이터 차이
area: dropTableItems     드랍 아이템 연결 차이
area: counts             전체 개수 차이
```

## 터미널 정적 검사

parity checker 파일이 존재하고 기본 구조가 있는지 확인하려면 아래를 실행한다.

위치: 프로젝트 루트

```bash
python tools/smoke/game/smoke_master_data_parity_checker.py
```

정상이라면 다음 문구가 나온다.

```txt
master-data parity checker smoke test passed
```

## 다음 단계

이 parity 검사가 통과하면 다음 단계에서 기존 JS 데이터와 API 데이터를 연결하는 어댑터를 만들 수 있다.

다음 단계 후보:

```txt
v087_master_data_runtime_adapter
```

이후에는 브라우저 게임이 기존 `src/data/*.js` 정적 데이터 대신 API master-data snapshot을 읽을 수 있도록 점진 전환한다.


### v087 note

`lightsabre`처럼 기본 발동확률이 없는 스킬은 `procRate: null`로 유지합니다. `python scripts/setup_dev_db.py --reset --seed --verify`를 다시 실행해야 DB에 반영됩니다.
