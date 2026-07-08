# Admin Create Lifecycle Guide

현재 기준: **v181 admin create lifecycle guard helper**

이 문서는 v180 생성 lifecycle guide를 설명하고, v181에서 추가된 삭제 차단 기준 표시도 함께 추적합니다.

## 목적

v179에서 `skillLevels`, `enhancementLevels`, `characterSkills`까지 신규 row 생성 apply가 열리면서, 관리자에서 생성→삭제→복원 전체 흐름을 브라우저로 확인해야 하는 단계가 되었습니다.

v180은 새 쓰기 기능을 크게 열지 않고, 기존 생성/삭제/복원 흐름을 더 안전하게 확인하기 위한 UI와 메타데이터를 추가합니다.

## 추가된 내용

- 관리자 페이지에 `신규 row 생성·삭제·복원 점검` 섹션 추가.
- 생성 설계를 불러온 도메인 기준으로 브라우저 점검 순서를 표시.
- 생성/삭제/복원 가능 여부를 도메인별로 표시.
- code 기반 도메인과 id 기반 도메인의 삭제/복원 key 표시.
- JSON/asset 잠금 필드 표시.
- combo guard 표시.
- 생성/삭제/복원 확인 문구 표시.
- change log action filter를 현재 실제 이력 액션 기준으로 정리.
- v181에서 삭제 preview 차단 기준과 변경 이력 action 바로가기 추가.

## change log action filter

v180부터 관리자 변경 이력 필터의 action 선택지는 실제 저장되는 action 값 기준입니다.

- `update`
- `rollback`
- `create`
- `create_delete`
- `create_delete_restore`

이제 생성 row를 삭제하거나 복원할 때, 변경 이력에서 `create` 또는 `create_delete` 이력을 더 쉽게 찾을 수 있습니다.

## 생성 lifecycle 메타데이터

`create-blueprint` 응답에 `createLifecycle` 정보를 추가했습니다.

포함 정보:

- `createApplyUnlocked`
- `createDeleteUnlocked`
- `createDeleteRestoreUnlocked`
- `identityMode`
- `deleteRestoreKey`
- `confirmTexts`
- `comboGuards`
- `lockedFields`
- `jsonAssetLocked`
- `browserCheckOrder`
- `deleteDependencyGuards`
- `deleteGuardMode`

## 안전 범위

- 새 DB schema 없음.
- DB reset / seed 필요 없음.
- 기존 게임 런타임 변경 없음.
- localStorage save key 변경 없음.
- 생성/삭제/복원 API의 확인 문구와 dev key guard 유지.
- JSON/asset 생성 입력 잠금 유지.

## 브라우저 확인 순서

관리자 페이지에서 도메인별로 아래 순서로 확인합니다.

1. `신규 row 생성 준비`에서 도메인 선택.
2. `생성 설계 불러오기` 클릭.
3. `신규 row 생성·삭제·복원 점검` 섹션에서 점검 순서 확인.
4. relation 후보와 combo guard 표시 확인.
5. 생성 초안 검증.
6. 실제 생성 적용.
7. 변경 이력에서 action `create` 필터로 생성 이력 확인.
8. 생성 row 삭제 미리보기/apply 확인.
9. 변경 이력에서 action `create_delete` 필터로 삭제 이력 확인.
10. 삭제 row 복원 미리보기/apply 확인.

## smoke

```bash
위치: 프로젝트 루트
node tools/smoke_admin_create_lifecycle_guide.js
```

```bash
위치: 프로젝트 루트
bash tools/run_smoke_core.sh
```
