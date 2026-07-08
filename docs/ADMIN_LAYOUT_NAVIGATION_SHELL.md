# Admin Layout Navigation Shell

## 목적

관리자 페이지가 길어지면서 기능을 찾기 어려워지는 문제를 줄이기 위해, 기존 `admin.html` 구조를 유지한 채 레이아웃만 정리했습니다.

## v172 변경 사항

- 상단 header를 sticky 형태로 고정했습니다.
- 왼쪽 sidebar를 추가했습니다.
- sidebar에서 주요 섹션으로 빠르게 이동할 수 있습니다.
- 주요 관리자 섹션에 접기/펼치기 버튼을 추가했습니다.
- 접힌 섹션 상태는 브라우저 localStorage에 저장됩니다.
- footer를 관리자 상태/버전 표시 영역으로 정리했습니다.
- 기존 관리자 기능, API 호출, smoke 확인 함수는 그대로 유지했습니다.


## v173 보강 사항

- sticky header 높이를 JS에서 계산해 sidebar top offset에 반영했습니다.
- 사이드바가 스크롤 중 header 아래로 숨어 보이지 않도록 `--admin-sticky-top` 값을 동적으로 보정합니다.
- 섹션 anchor 이동 시 header에 제목이 가려지지 않도록 `scroll-margin-top`을 적용했습니다.
- `필드 용어 도움말`, `신규 row 생성 준비`, `관리자 변경 이력`은 기본 상태를 접기로 변경했습니다.
- 접힌 섹션은 amber 계열 배경/테두리/버튼색을 적용해 펼쳐진 섹션과 더 쉽게 구분되게 했습니다.
- 접기 상태 저장 key를 V2로 분리해 v173 기본 접기 정책이 새로 적용되게 했습니다.

## 안전 범위

- DB reset / seed 필요 없음.
- DB schema 변경 없음.
- `.env`, `.gitignore` 변경 없음.
- 기존 edit/create/delete/restore 기능은 변경하지 않았습니다.
- 관리자 UI 구조와 표시 방식만 정리했습니다.

## 확인 함수

브라우저 개발자도구 Console에서 아래를 확인할 수 있습니다.

```js
checkAdminReadOnlyPageReady().layoutShellReady
```

```js
getAdminLayoutShellReadiness()
```

정상이라면 `layoutReady`, `sidebarReady`, `collapseReady`, `footerReady`, `stickyOffsetReady`가 true로 표시됩니다. 첫 진입 기준으로 `defaultCollapsedReady`도 true면 기본 접기 정책이 적용된 상태입니다.
