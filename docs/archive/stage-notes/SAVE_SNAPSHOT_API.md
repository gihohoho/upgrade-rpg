# v099 Save Snapshot API

## 목적

`master-data`는 PostgreSQL/FastAPI에서 읽는 흐름까지 연결되었다. 다음 단계는 유저 진행 데이터를 한 번에 정규화하기 전에, 현재 브라우저 `localStorage` 저장값을 그대로 DB에 보관하는 안전한 다리 구조를 만드는 것이다.

현재 브라우저 저장 키:

```txt
idleRpgSaveV22
```

## 이번 단계에서 하는 일

현재 localStorage 저장 구조를 바로 깨지 않기 위해, `snapshot_json`에 원본 payload를 그대로 저장한다.

```txt
localStorage idleRpgSaveV22
→ POST /api/v1/game/save
→ user_save_snapshots.snapshot_json
```

불러올 때도 아직 게임에 자동 적용하지 않고, API 응답으로만 확인한다.

```txt
GET /api/v1/game/load
→ 마지막 저장 snapshot 반환
```

## API

### POST /api/v1/game/save

위치: FastAPI 서버

```json
{
  "saveVersion": 5,
  "clientSaveKey": "idleRpgSaveV22",
  "slotKey": "default",
  "snapshot": {},
  "summary": {},
  "source": "localStorage-manual-push",
  "note": null
}
```

### GET /api/v1/game/load

```txt
/api/v1/game/load?slotKey=default
```

응답의 `payload.snapshot`에 저장했던 원본 save payload가 들어온다.

## 브라우저 Console 함수

FastAPI 서버가 켜진 상태에서 게임 화면 Console에서 실행한다.

```js
await checkBackendSaveSnapshotBridge();
await pushLocalSaveToBackend();
await loadBackendSaveSnapshot();
```

주의: `loadBackendSaveSnapshot()`은 아직 게임에 적용하지 않는다. 저장된 값을 확인만 한다.

## 확인 명령어

### 정적 검사

위치: 프로젝트 루트

```bash
python tools/smoke_save_snapshot_api_structure.py
node tools/smoke_save_data_bridge.js
```

### 실제 API 검사

FastAPI 서버 실행:

위치: backend 폴더 + 가상환경 activate 상태

```bash
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

새 터미널에서:

위치: backend 폴더 + 가상환경 activate 상태

```bash
source .venv/Scripts/activate
python scripts/check_save_snapshot_api.py
```

## 다음 단계

이 API가 안정적으로 동작하면, 다음 단계에서 브라우저 수동 저장 버튼이나 자동 저장 흐름에 백엔드 저장을 선택적으로 연결한다. 기본 localStorage 저장은 계속 유지한다.
