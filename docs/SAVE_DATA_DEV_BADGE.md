# SAVE DATA 개발자 배지

v101에서 추가된 로컬 개발용 저장 상태 배지입니다.

## 목적

수동 저장 버튼을 눌렀을 때 기존 `localStorage` 저장뿐 아니라 백엔드 DB 저장까지 성공했는지 브라우저 화면에서 바로 확인하기 위한 도구입니다.

기존 게임 저장 구조는 그대로 유지됩니다.

```txt
수동 저장 버튼
→ localStorage 저장
→ 백엔드 DB 저장 시도
→ SAVE DATA 배지에 상태 표시
```

## 표시 위치

로컬 개발 환경에서 화면에 작은 `SAVE DATA` 배지가 표시됩니다.

대상 환경:

```txt
file://
localhost
127.0.0.1
```

## 표시 내용

```txt
SAVE DATA synced
mode: manual_dual slot: default
Lv:1 · G:100 · Inv:12 · Sto:3
loaded: loaded · v5
updated: 16:45:10 · saved: 16:45:08
```

주요 상태:

| state | 의미 |
|---|---|
| `synced` | 백엔드 DB 저장 성공 |
| `never_synced` | 아직 백엔드 저장을 한 적 없음 |
| `failed_fallback_to_local_storage` | 로컬 저장은 성공했지만 백엔드 저장 실패 |
| `skipped_local_only_mode` | localStorage 전용 모드라 백엔드 저장을 건너뜀 |

## 버튼 역할

| 버튼 | 역할 |
|---|---|
| `sync` | 현재 localStorage 저장값을 즉시 백엔드 DB에 저장 |
| `load` | 백엔드 DB에 저장된 세이브 스냅샷을 조회만 함. 아직 게임에 적용하지 않음 |
| `dual` | 수동 저장 시 localStorage와 백엔드 DB에 함께 저장 |
| `local` | 기존 방식처럼 localStorage에만 저장 |
| `hide SAVE` | 배지를 접음 |
| `show SAVE` | 접힌 배지를 다시 펼침 |

## Console 함수

브라우저 개발자도구 Console에서 사용할 수 있습니다.

```js
refreshBackendSaveDataDevBadge();
showBackendSaveDataDevBadge();
hideBackendSaveDataDevBadge();
toggleBackendSaveDataDevBadge();
```

저장 정책/상태 확인 함수는 v100에서 추가된 것을 그대로 사용합니다.

```js
getBackendSaveSyncPolicy();
getBackendSaveSyncStatus();
enableBackendSaveDualWrite();
disableBackendSaveDualWrite();
await syncLatestLocalSaveToBackend();
await loadBackendSaveSnapshot();
```

## 주의

`load` 버튼은 백엔드 저장값을 **조회만** 합니다.

아직 백엔드 저장값을 실제 게임 상태에 복원하지 않습니다. 복원 기능은 다음 단계에서 별도로 안전장치와 함께 추가합니다.

## v102: 기본 모드와 테스트 혼동 방지

v102부터 로컬 개발 환경에서 SAVE DATA 기본 모드는 `manual_dual`입니다.

v101 테스트 중 `local` 버튼을 누른 상태가 localStorage에 남아 있으면 다음 접속 때도 계속 local로 시작할 수 있었습니다. v102는 최초 적용 시 그 이전 local 상태를 한 번 `manual_dual`로 되돌립니다. 이후 사용자가 다시 `local` 버튼을 누르면 그 선택은 유지됩니다.

버튼 이름도 명확하게 바꿨습니다.

- `sync DB`: 현재 localStorage 저장값을 백엔드 DB로 즉시 전송합니다.
- `load DB`: 백엔드 DB 저장값을 조회만 합니다. 아직 게임에 적용하지 않습니다.
- `dual`: 성장/시스템 → 수동 저장 시 localStorage와 백엔드 DB에 함께 저장합니다.
- `local`: 성장/시스템 → 수동 저장 시 localStorage에만 저장합니다.

수동 저장에는 60초 쿨타임이 있습니다. 쿨타임 중 다시 누르면 실제 저장 로직이 실행되지 않기 때문에 DB 저장도 시도하지 않습니다. 이 경우 배지는 `skipped_manual_save_cooldown`으로 표시합니다.

`skipped_local_only_mode`는 현재 `local` 모드라서 백엔드 저장을 일부러 건너뛰었다는 뜻입니다. DB 저장 테스트는 반드시 `dual` 버튼이 활성화된 상태에서 진행합니다.

## v107: 복구 미리보기 버튼 추가

v107부터 SAVE DATA 배지에 복구 관련 버튼이 추가됐습니다.

| 버튼 | 역할 |
|---|---|
| `preview` | Console 명령어 없이 DB 세이브 복구 미리보기 모달을 엽니다. |
| `backup` | 가장 최근 복구 전 백업을 localStorage로 되돌립니다. 누르면 브라우저 확인창이 먼저 뜹니다. |

배지에는 `restore: ... · backups:n` 줄도 표시됩니다. 복구 완료 후에는 `restored_needs_reload`, 백업 복구 후에는 `backup_restored_needs_reload` 상태를 확인할 수 있습니다.

주의: `preview`에서 DB 세이브로 복구해도 즉시 게임 화면 상태가 바뀌는 것은 아닙니다. 기존 안전장치대로 localStorage만 바꾸고, 새로고침 후 적용됩니다.

## v110: 저장 후 무결성 검증

v110부터 `sync DB`와 수동 저장의 백엔드 이중 저장은 저장 직후 DB 세이브를 다시 조회해서 localStorage와 완전히 같은지 확인합니다.

| state | 의미 |
|---|---|
| `synced_verified` | DB 저장 성공 + DB 재조회 후 localStorage와 완전 동일 확인 |
| `saved_verify_failed` | DB 저장 후 검증 실패. `preview`로 차이를 확인해야 함 |

추가 Console 함수:

```js
await verifyBackendSaveSnapshotIntegrity();
await pushLocalSaveToBackendAndVerify();
await checkBackendSaveIntegrityReady();
```
