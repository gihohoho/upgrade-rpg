# Admin Collapsed Panel Style Fix

## 목적

v173에서 접힌 섹션 색상 구분을 추가했지만, `.section` 기반 섹션과 `.filter-panel` / `.field-help-panel` 기반 섹션의 내부 구조가 달라 일부 접힌 탭이 서로 다르게 보였습니다.

v174에서는 접힌 상태 스타일을 공통 규칙으로 보정해, 어떤 관리자 탭을 접어도 같은 카드 형태로 보이게 했습니다.

## v174 변경 사항

- `.filter-panel`과 `.field-help-panel`이 접혔을 때 내부 padding 때문에 header 색상이 안쪽에만 들어가던 문제를 수정했습니다.
- 접힌 filter/help 패널은 섹션 전체가 같은 amber 계열 배경/테두리로 보이게 했습니다.
- 접힌 패널 header는 `.section-header` 방식과 비슷하게 전체 너비를 차지하도록 통일했습니다.
- `getAdminLayoutShellReadiness()`에 `collapsedPanelStyleReady` 상태를 추가했습니다.

## 안전 범위

- DB reset / seed 필요 없음.
- DB schema 변경 없음.
- `.env`, `.gitignore` 변경 없음.
- 관리자 기능 동작은 변경하지 않고 접힌 상태 CSS/표시만 보강했습니다.

## 확인 함수

```js
checkAdminReadOnlyPageReady().layoutShellReady
```

```js
getAdminLayoutShellReadiness().collapsedPanelStyleReady
```
