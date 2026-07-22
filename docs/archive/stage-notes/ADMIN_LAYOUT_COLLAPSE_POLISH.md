# Admin Layout Collapse Polish

## 목적

관리자 페이지가 길어진 상태에서 sidebar와 sticky header가 겹치는 문제를 줄이고, 기본 접기 상태와 접힌 섹션 표시를 더 명확하게 정리했습니다.

## v173 변경 사항

- sticky header 높이를 측정해 sidebar top offset을 자동 보정합니다.
- anchor 이동 시 섹션 제목이 header에 가려지지 않도록 scroll margin을 적용했습니다.
- 아래 섹션은 기본 상태를 접기로 변경했습니다.
  - 필드 용어 도움말
  - 신규 row 생성 준비
  - 관리자 변경 이력
- 접힌 섹션은 amber 계열 배경/테두리/버튼색으로 표시해 펼침 상태와 구분되게 했습니다.
- 접기 상태 localStorage key를 `upgradeRpgAdminCollapsedSectionsV2`로 분리했습니다.

## 안전 범위

- DB reset / seed 필요 없음.
- DB schema 변경 없음.
- `.env`, `.gitignore` 변경 없음.
- 관리자 기능 동작은 변경하지 않고 레이아웃/표시 상태만 보강했습니다.

## 확인 함수

```js
checkAdminReadOnlyPageReady().layoutShellReady
```

```js
getAdminLayoutShellReadiness()
```

```js
getAdminDefaultCollapsedSectionKeys()
```

## v174 추가 보정

- `.section` 기반 섹션은 정상적으로 접힌 색상이 보였지만, `.filter-panel` / `.field-help-panel` 기반 섹션은 내부 padding 때문에 header만 안쪽에 색이 들어가는 문제가 있었습니다.
- 접힌 상태에서는 filter/help 패널 padding을 제거하고, direct `.filter-title` header가 전체 너비를 차지하도록 보정했습니다.
- `필드 용어 도움말`, `신규 row 생성 준비`, `관리자 쓰기 dev key 잠금`, `최근 세이브 스냅샷 필터`처럼 filter/help 구조인 탭도 같은 스타일로 보입니다.
