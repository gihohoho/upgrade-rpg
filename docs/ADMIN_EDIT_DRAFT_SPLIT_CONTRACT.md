# Admin Edit Draft Split Contract

버전: **v190 admin edit draft split contract**

## 목적

`edit draft` 기능을 바로 외부 파일로 분리하지 않고, 실제 분리 전에 필요한 계약을 먼저 고정합니다.

후보 파일:

```txt
src/api/admin/admin-edit-draft.js
```

계약 상태:

```txt
contract-frozen-v190
```

## 이번 단계에서 고정한 것

- 편집 초안 렌더링 함수
- 편집 초안 값 읽기/초기화 함수
- 편집 preview/apply 함수
- guarded edit 확인 문구
- high risk 확인 문구
- relation select helper
- relation select dependent filter
- field value hint helper
- draft review helper
- impact guide helper
- 결과 렌더링 helper
- DOM target
- delegated action

## 확인 문구

```txt
APPLY MASTER DATA EDIT
```

```txt
HIGH RISK EDIT
```

## 새 확인 함수

브라우저 개발자도구 Console에서 확인할 수 있습니다.

```js
getAdminEditDraftSplitContractReadiness()
```

또는 전체 readiness에서 확인할 수 있습니다.

```js
checkAdminReadOnlyPageReady().editDraftSplitContractReady
```

예상값:

```txt
true
```

## 다음 단계

다음 단계에서는 실제 파일을 만들 수 있습니다.

```txt
src/api/admin/admin-edit-draft.js
```

다만 `edit draft`는 아래 기능과 연결되어 있어서 실제 분리는 한 번에 크게 하지 않는 것이 안전합니다.

- relation select
- value hint
- impact guide
- guarded edit apply
- high risk confirm
- master detail render

따라서 v191에서는 `edit draft` 실제 분리 1단계만 진행하는 것을 추천합니다.

## DB reset / seed

필요 없습니다.

- DB schema 변경 없음
- seed 재실행 필요 없음
- `.env`, `.gitignore` 변경 없음
