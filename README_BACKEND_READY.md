## v106
- 백엔드 DB 세이브를 localStorage에 덮어쓰기 전에 미리보기 모달로 비교할 수 있게 했습니다.
- 복구 실행 전 현재 localStorage 세이브를 자동 백업합니다.
- 복구 후 바로 런타임에 적용하지 않고 새로고침 후 적용되도록 했습니다.

# RPG 백엔드 분리 준비 구조

이 ZIP은 기존 게임 기능을 유지하면서, 백엔드/관리자 분리를 쉽게 하기 위해 파일 위치와 역할을 단계적으로 정리한 버전입니다.

현재 v188 기준으로는 관리자 layout shell과 change logs가 외부 JS 파일로 1차 분리되어 있고, create lifecycle 실제 분리 전 계약이 고정되어 있습니다.

## 먼저 읽을 문서

```txt
README.md
```

전체 안내 문서입니다.

```txt
docs/BACKEND_SPLIT_STAGE2_PLAN.md
```

백엔드 분리 준비 2차 작업 계획서입니다.

```txt
docs/BACKEND_SPLIT_CHECKLIST.md
```

1~5순위 진행 상태와 완료 기준 체크리스트입니다.

```txt
docs/CODE_MAP.md
```

파일별 역할과 주요 함수 위치를 빠르게 찾기 위한 탐색 지도입니다.

```txt
docs/ADMIN_PAGE_REQUIREMENTS.md
```

관리자 페이지에서 수정 가능해야 할 항목 정리입니다.

```txt
src/state/STATE_SPLIT_READY.md
```

이번 1순위 상태 분리 작업의 상세 기록입니다.

## 현재 폴더 구조

```txt
index.html
README.md
README_BACKEND_READY.md
docs/
  BACKEND_SPLIT_STAGE2_PLAN.md
  BACKEND_SPLIT_CHECKLIST.md
  CODE_MAP.md
  ADMIN_PAGE_REQUIREMENTS.md
  DECISION_LOG.md
  CHANGELOG.md
src/
  styles/
    style.css
  state/
    game-state.js
    README.md
    STATE_SPLIT_READY.md
  data/
    bosses.js
    zones.js
  systems/
    stat-system.js
    item-system.js
    combat-system.js
  ui/
    render-ui.js
  app/
    main.js
  api/
    API_PLAN.md
```

## 각 폴더 역할

### src/state/game-state.js

게임의 현재 상태를 담습니다.

이번 버전에서 아래처럼 나뉘었습니다.

```txt
gameState.server  = 서버/DB 저장 후보
gameState.client  = 화면에서만 필요한 상태
gameState.runtime = 실행 중 임시 상태
```

### src/data/bosses.js

보스 데이터와 보스 드랍 관련 설정이 들어 있습니다.

다음 작업에서 가장 먼저 정리할 파일입니다.

### src/data/zones.js

필드존 데이터가 들어 있습니다.

백엔드로 갈 때 서버 DB나 JSON 데이터로 옮기기 좋은 후보입니다.

### src/systems/stat-system.js

공격력, 공격속도, 장비 스탯, 강화 확률 같은 계산 함수가 들어 있습니다.

### src/systems/item-system.js

아이템 장착, 해제, 강화, 버리기, 보관함 이동 로직이 들어 있습니다.

### src/systems/combat-system.js

전투, 필드/보스 이동, 처치, 드랍 처리 로직이 들어 있습니다.

### src/ui/render-ui.js

화면 표시, 툴팁, 인벤토리 그리기, HUD 갱신 로직이 들어 있습니다.

### src/app/main.js

게임 시작, 저장/불러오기, 테스트 지급 모달 같은 앱 실행 관련 코드가 들어 있습니다.

## 중요한 주의사항

현재 코드는 아직 `import/export` 방식이 아니라, HTML에서 스크립트를 순서대로 읽는 방식입니다.
그래서 `index.html` 아래쪽의 script 순서를 바꾸면 게임이 깨질 수 있습니다.

현재 순서:

1. `state/game-state.js`
2. `data/bosses.js`
3. `data/zones.js`
4. `systems/stat-system.js`
5. `ui/render-ui.js`
6. `systems/item-system.js`
7. `systems/combat-system.js`
8. `app/main.js`

## 다음 작업 추천 순서

1. `bosses.js` 순수 데이터화
2. 캐릭터별 스킬 구조 준비
3. `systems` 함수와 UI 분리
4. API 응답 형태 확정
5. DB 추출용 JSON 생성
6. FastAPI 저장/불러오기 API 연결


---

## v074 API 응답 형태 확정

5순위 작업으로 FastAPI 응답 형태를 확정했습니다.

참고 파일:

```txt
docs/API_RESPONSE_CONTRACT.md
src/api/API_PLAN.md
src/api/api-response-contract.js
```

이번 작업은 현재 브라우저 게임 동작을 바꾸지 않는 문서/계약 작업입니다.

## v084 note

- `/api/v1/game/master-data` 기본 응답에서 최상위 asset 필드뿐 아니라 `options`, `conditions`, `rules`, `raw` 같은 중첩 JSON 안의 `data:image...` 문자열도 제거합니다.
- asset 문자열이 필요한 경우에는 `?includeAssets=true`를 사용합니다.



## v086 - Master Data Parity Checker

`backend/scripts/check_master_data_parity.py`로 JS seed JSON과 FastAPI master-data API 응답이 같은지 비교할 수 있습니다.

위치: backend 폴더 + 가상환경 activate 상태

```bash
python scripts/check_master_data_parity.py
python scripts/check_master_data_parity.py --include-assets
```


### v087 note

`lightsabre`처럼 기본 발동확률이 없는 스킬은 `procRate: null`로 유지합니다. `python scripts/setup_dev_db.py --reset --seed --verify`를 다시 실행해야 DB에 반영됩니다.


## v088 - 프론트 master-data 어댑터

브라우저에서 FastAPI master-data 응답을 기존 JS 데이터 구조와 비슷하게 변환하는 `src/api/master-data-adapter.js`가 추가되었습니다. 실제 런타임 교체는 아직 하지 않습니다.

위치: 프로젝트 루트

```bash
node tools/smoke_master_data_adapter.js
```


## v089 - Backend master-data runtime switch

- 기본 OFF 상태의 브라우저 런타임 전환 플래그를 추가했습니다.
- `enableBackendMasterDataMode()`를 실행하면 다음 페이지 로드부터 FastAPI master-data를 기존 게임 데이터 형태로 주입합니다.
- 실패 시 기존 JS 데이터로 fallback하므로 현재 게임 실행 안전성을 유지합니다.

## v090 note

백엔드 master-data 런타임 모드 검증 도구가 추가되었습니다.

- `checkBackendMasterDataRuntimeIntegrity({ requireBackendMode: true })`
- `getBackendMasterDataRuntimeDebugSnapshot()`
- `node tools/smoke_master_data_runtime_validator.js`

이 단계는 실제 게임 로직을 바꾸지 않고, API 데이터 주입 후 전역 데이터와 핵심 DOM이 정상인지 확인하는 안전 점검 단계입니다.

## v091 note

백엔드 master-data 모드가 실제 브라우저 화면에서 정상적으로 보스/필드/장비지급/인벤토리 데이터를 그리는지 확인하기 위한 체크리스트 도구가 추가되었습니다.

위치: **프로젝트 루트**

```bash
node tools/smoke_master_data_browser_checklist.js
```

브라우저 Console:

```js
runBackendMasterDataBrowserChecklist();
```
## v092 - Backend master-data auto boot policy

- 브라우저 시작 시 백엔드 master-data를 자동으로 시도하는 `auto` 정책을 추가했습니다.
- FastAPI 요청 실패 시 기존 JS 데이터로 자동 fallback합니다.
- 기본 API 요청에서는 긴 image/data URL asset을 제외하고, 필요한 이미지는 이미 로드된 정적 JS 데이터에서 보정합니다.
- 확인 스크립트: `node tools/smoke_master_data_auto_boot_policy.js`



## v093 - Browser checklist optional modal fix

백엔드 master-data 자동 적용 상태는 정상인데 `#test-special-item-modal` 요소가 없다는 이유로 브라우저 체크리스트가 실패하던 문제를 수정했습니다.

이 요소는 필수 DOM이 아니라 선택/동적 모달 요소로 취급합니다. 이제 해당 요소가 없어도 `warn`으로만 표시되고, 다른 필수 검사가 통과하면 `runBackendMasterDataBrowserChecklist()`의 전체 `ok`는 `true`가 됩니다.


### v093 추가 보정 - master-data bridge timeout summary

`checkBackendMasterData()`가 summary를 만들 때 `timeoutMs` 지역 변수를 직접 참조하던 문제를 수정했습니다. 이제 `snapshot.timeoutMs`를 사용하므로 브라우저/스모크 테스트에서 `ReferenceError: timeoutMs is not defined`가 발생하지 않습니다.


### v094 - Field zone asset fallback

- 백엔드 master-data 자동 적용 시 필드존 이미지가 `undefined`로 렌더링되지 않도록 보정했습니다.
- 기본 master-data 응답은 여전히 assets 제외 정책을 유지하며, 필요한 이미지는 기존 정적 JS 데이터에서 보정합니다.

## v095 메모 - master-data 개발자 배지

브라우저 로컬 개발 환경에서 화면 하단에 master-data 상태 배지가 표시된다. 현재 `auto/static/backend`, `applied/fallback`, assets 포함 여부, 주요 데이터 개수를 빠르게 확인할 수 있다. 숨기려면 Console에서 `hideBackendMasterDataDevBadge()`를 실행한다.



## v096 메모 - master-data 배지 위치 보정

- master-data 개발자 배지를 하단 HUD 중앙 능력치 패널 오른쪽으로 이동했다.
- 왼쪽 프로필 사진과 반대편에 배치해 현재 백엔드 데이터 상태를 화면에서 바로 볼 수 있다.
- `hide` 버튼을 눌러 사라진 배지는 Console에서 `showBackendMasterDataDevBadge()`로 다시 표시할 수 있다.

## v097 메모 - master-data 개발자 배지 개선

- 배지 버튼 줄 넘침을 줄이고 hide/show 토글을 배지 위쪽 별도 버튼으로 분리했습니다.
- 숨김 상태에서도 `show MD` 버튼으로 다시 표시할 수 있습니다.
- 현재 모드(auto/static)에 활성 스타일을 표시합니다.


## v098 메모 - master-data 배지 토글 정렬

- 배지 토글 문구를 `hide MD` / `show MD`로 변경했습니다.
- 토글 버튼을 MASTER DATA 배지 상단 정가운데에 탭처럼 배치했습니다.
- 배지를 숨겨도 화면 안의 `show MD` 버튼으로 다시 펼칠 수 있습니다.
- 이 수정은 프론트 개발자용 UI만 바꾸므로 DB reset/seed import는 필요 없습니다.

### v099 save snapshot API bridge

유저 진행 데이터 마이그레이션의 첫 단계로 `idleRpgSaveV22` localStorage 원본을 PostgreSQL `user_save_snapshots`에 저장/조회하는 API와 브라우저 테스트 함수를 추가했습니다. 아직 게임 로딩 흐름은 localStorage를 유지합니다.



## v100 - Save Data Dual Write

수동 저장 버튼을 기존 localStorage 저장과 백엔드 `/api/v1/game/save` 저장에 동시에 연결했습니다. 백엔드 저장 실패 시에도 기존 localStorage 저장은 유지됩니다.

위치: 프로젝트 루트

```bash
node tools/smoke_save_data_dual_write.js
```


## v101 - SAVE DATA 개발자 배지

수동 저장 시 백엔드 DB 저장 성공/실패 상태를 브라우저 화면에서 확인할 수 있는 개발자용 배지를 추가했습니다.

## v102 SAVE DATA test note

If SAVE DATA shows `skipped_local_only_mode`, click `dual` once and try `성장/시스템 → 수동 저장` again after the 60 second manual-save cooldown. During cooldown, the badge shows `skipped_manual_save_cooldown`.


## v186 완료

- 관리자 change logs 분리 전 계약 고정.
- 실제 DB schema/backend env 변경 없음.
- DB reset / seed 필요 없음.


## v188 완료

- `create lifecycle` 실제 분리 전 계약을 `contract-frozen-v188` 상태로 고정
- 다음 후보 파일 `src/api/admin/admin-create-lifecycle.js` 고정
- 생성 초안/생성 apply/생성→삭제→복원 batch check 함수 목록 고정
- 확인 문구/DOM target/delegated action 목록 고정
- 새 smoke `tools/smoke_admin_create_lifecycle_split_contract.js` 추가
- 실제 JS 파일 분리는 아직 하지 않음
- DB reset / seed 필요 없음
