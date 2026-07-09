# Upgrade RPG v191 패키지

현재 안정 버전: **v191 admin edit draft split**

새 채팅 인수인계 ZIP: **rpg_v191_admin_edit_draft_split_ready.zip**

## 요약

v191에서는 관리자 `edit draft` 구현을 실제 외부 JS 파일로 1차 분리했습니다.

새 파일:

- `src/api/admin/admin-edit-draft.js`

기존 호환 wrapper는 `src/api/admin-page-readonly.js`에 유지했습니다.

## 현재 관리자 JS 분리 상태

- `src/api/game-api-client.js` — 기존 외부 API client
- `src/api/admin-layout-shell.js` — v185 분리 완료
- `src/api/admin/admin-change-logs.js` — v187 분리 완료
- `src/api/admin/admin-create-lifecycle.js` — v189.1 hotfix 포함 분리 완료
- `src/api/admin/admin-edit-draft.js` — v191 분리 완료
- `src/api/admin-page-readonly.js` — bootstrap/bindEvents/window wrapper 중심 entry 파일

## v191에서 분리한 edit draft 기능

- 편집 초안 렌더링
- 편집 초안 값 읽기/초기화
- relation select 검색/연동
- impact guide
- draft review
- preview/apply 호출
- stale guard 결과 렌더링
- relation value display/open target helper

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상값:

```txt
v191.admin-edit-draft-split
```

```js
checkAdminReadOnlyPageReady().editDraftExternalReady
```

예상값:

```txt
true
```

```js
window.RpgAdminEditDraft.VERSION
```

예상값:

```txt
v191.admin-edit-draft-split
```

## 검증

- `bash tools/run_smoke_core.sh` 통과
- `bash tools/run_smoke_all.sh` 통과
- `node --check` 주요 관리자 JS 통과
- `python -m compileall -q backend/app` 통과

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음

## 다음 추천 단계

다음 v192는 **master detail/catalog 분리 전 계약 고정**이 좋습니다.

바로 큰 분리를 하기보다 아래 계약을 먼저 고정하는 방식이 안전합니다.

- master catalog table/render/pagination 함수 목록
- master detail open/render 함수 목록
- master relation render 함수 목록
- API verify helper 목록
- window export 목록
- DOM target 목록
- 다음 후보 파일명: `src/api/admin/admin-master-detail.js` 또는 `src/api/admin/admin-master-catalog.js`
