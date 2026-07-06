# v093 Backend Master Data Browser Checklist

`v090`까지는 백엔드 master-data 모드가 브라우저 런타임에 주입됐는지 자동 검증했다.
`v091`은 실제 화면 체크리스트를 추가했고, `v093`은 실제 화면 구조에 맞춰 선택 DOM 검사를 보정한다.

## 목적

- 백엔드 master-data 모드가 실제 브라우저에서 적용됐는지 확인한다.
- 일반보스, 특수보스, 필드존, 장비지급, 인벤토리의 핵심 DOM과 렌더링 상태를 확인한다.
- 아직 실제 게임 로직은 바꾸지 않는다.
- 기본 JS 데이터 모드와 백엔드 데이터 모드를 안전하게 비교하기 위한 수동 QA 흐름을 제공한다.

## 정적 검사

위치: **프로젝트 루트**

```bash
node tools/smoke_master_data_browser_checklist.js
```

정상 출력:

```txt
master-data browser checklist smoke test passed
```

## 브라우저 검사 순서

FastAPI 서버를 먼저 켠다.

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

게임 화면을 연 뒤 브라우저 개발자도구 Console에서 실행한다.

```js
enableBackendMasterDataMode();
```

페이지가 자동으로 새로고침되면 다시 Console에서 실행한다.

```js
runBackendMasterDataBrowserChecklist();
```

정상이라면 반환 객체의 `ok`가 `true`이다.

```js
const report = runBackendMasterDataBrowserChecklist();
report.ok;
```

강제로 실패 시 에러를 던지게 하려면 다음을 쓴다.

```js
assertBackendMasterDataBrowserChecklist();
```

수동 체크리스트만 출력하려면 다음을 쓴다.

```js
printBackendMasterDataManualChecklist();
```

## 검사하는 항목

자동 검사:

- 백엔드 master-data runtime switch 로딩 여부
- runtime validator 로딩 여부
- 백엔드 데이터 모드 ON 여부
- 백엔드 데이터 적용 완료 여부
- characters, skills, itemTemplates, normalBosses, specialBosses, fieldZones 최소 개수
- 핵심 DOM 존재 여부
- 선택 DOM 존재 여부(`#test-special-item-modal`은 일부 빌드에서 동적 생성/생략 가능하므로 경고로만 표시)
- 일반보스 그리드 렌더링 여부
- 특수보스 그리드 렌더링 여부
- 필드존 목록 렌더링 여부
- 인벤토리/장비 슬롯 렌더링 여부
- 첫 일반보스/특수보스/필드 샘플 값
- `lightsabre`의 `procRate`가 `null`로 유지되는지

수동 확인:

1. 보스존 입장 버튼 클릭
2. 일반보스 목록, 툴팁, 소환 클릭 확인
3. 특수보스 패널 클릭
4. 특수보스 목록, 쿨타임 표시, 소환 제한 확인
5. 필드존 선택 클릭
6. 필드 목록, 입장 조건, 툴팁 확인
7. 장비지급/특수보스 장비지급 모달 확인
8. 인벤토리 슬롯/장비 슬롯 확인
9. `disableBackendMasterDataMode()`로 OFF 복귀 확인

## 옵션

기본값:

```js
runBackendMasterDataBrowserChecklist({
  requireBackendMode: true,
  refreshPanels: true,
  log: true,
});
```

기존 JS 모드에서도 구조만 점검하려면:

```js
runBackendMasterDataBrowserChecklist({ requireBackendMode: false });
```

패널을 다시 렌더링하지 않고 현재 화면만 검사하려면:

```js
runBackendMasterDataBrowserChecklist({ refreshPanels: false });
```

## 주의

이 도구는 게임 데이터를 바꾸지 않는다. 다만 `refreshPanels: true`일 때 `renderUI`, `renderBossZone`, `renderSpecialBossZone`, `renderFieldZone` 등을 호출해서 화면 목록을 다시 그린다.


## v093 보정 사항

브라우저 검증에서 `#test-special-item-modal` 요소가 없다는 이유만으로 전체 체크리스트가 실패하던 문제를 수정했다.

이 요소는 특수 장비 지급 테스트 모달과 관련된 선택 DOM이며, 현재 구조에서는 `openTestSpecialItemModal()` 함수가 존재하고 실제 클릭 동작이 가능하면 필수 실패로 보지 않는다. 따라서 v093부터는 다음처럼 처리한다.

- 필수 DOM: `fail` 유지
- `#test-special-item-modal`: 없으면 `warn`, 있으면 `pass`
- `warn`만 있는 경우 전체 `ok`는 `true` 유지
