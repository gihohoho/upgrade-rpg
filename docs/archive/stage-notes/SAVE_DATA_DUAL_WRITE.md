# v100 Save Data Dual Write

이번 단계는 기존 `localStorage` 저장을 유지하면서, **수동 저장 버튼을 눌렀을 때 백엔드 DB에도 세이브 스냅샷을 저장**하는 단계입니다.

```txt
수동 저장 버튼 클릭
→ 기존 localStorage 저장 완료
→ FastAPI /api/v1/game/save 저장 시도
→ 성공하면 DB에도 저장
→ 실패해도 localStorage 저장은 유지
```

## 기본 모드

기본 모드는 `manual_dual`입니다.

```txt
manual_dual: 수동 저장 시 localStorage + backend DB 이중 저장
local_only: 기존 localStorage 저장만 사용
```

브라우저 Console에서 현재 정책을 확인할 수 있습니다.

```js
getBackendSaveSyncPolicy();
getBackendSaveSyncStatus();
```

## 모드 변경

백엔드 이중 저장 켜기:

```js
enableBackendSaveDualWrite();
```

로컬 저장 전용으로 끄기:

```js
disableBackendSaveDualWrite();
```

## 수동 동기화

현재 localStorage 저장값을 바로 백엔드로 보내려면:

```js
await syncLatestLocalSaveToBackend();
```

저장 브릿지 상태 확인:

```js
await checkBackendSaveSyncPolicy();
```

## 실패 처리

백엔드 저장 실패는 게임 저장 실패가 아닙니다.

```txt
localStorage 저장 성공
backend DB 저장 실패
→ 게임 진행 데이터는 브라우저에 안전하게 남아 있음
→ 로그에 백엔드 저장 실패 안내만 표시
```

## 실행 확인

위치: **프로젝트 루트**

```bash
node tools/smoke/game/smoke_save_data_dual_write.js
```

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

게임 화면에서 수동 저장 버튼을 누른 뒤 Console에서 확인합니다.

```js
getBackendSaveSyncStatus();
await loadBackendSaveSnapshot();
```

## v102: 테스트 기준 정리

DB 저장 테스트는 `dual` 모드에서 진행합니다.

1. SAVE DATA 배지에서 `dual` 버튼이 활성화되어 있는지 확인합니다.
2. 성장/시스템 → 수동 저장을 누릅니다.
3. SAVE DATA 배지가 `synced`로 바뀌는지 확인합니다.

`local` 모드는 백엔드 저장을 끄는 안전 모드입니다. 이 상태에서 성장/시스템 → 수동 저장을 누르면 localStorage 저장만 하고 DB 저장은 시도하지 않으며, 상태는 `skipped_local_only_mode`가 됩니다.

수동 저장에는 60초 쿨타임이 있으므로 연속 테스트 중에는 `sync DB` 버튼으로 DB 전송만 따로 확인할 수 있습니다.
