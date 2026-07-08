# Admin Create Lifecycle Split

## 버전

v189 admin create lifecycle split

## 목적

v188에서 고정한 `create lifecycle` 계약을 유지한 채, 생성 설계/초안/preview/apply/생성→삭제→복원 batch check 구현을 `admin-page-readonly.js` 밖으로 1차 분리했습니다.

## 변경 파일

- `src/api/admin/admin-create-lifecycle.js` 신규 추가
- `admin.html` script 순서 갱신
- `src/api/admin-page-readonly.js`는 기존 window export 호환 wrapper 유지
- `tools/smoke_admin_create_lifecycle_split.js` 신규 추가
- `tools/run_smoke_core.sh`에 신규 smoke 포함

## script 순서

```txt
src/api/game-api-client.js
src/api/admin-layout-shell.js
src/api/admin/admin-change-logs.js
src/api/admin/admin-create-lifecycle.js
src/api/admin-page-readonly.js
```

## 분리한 기능

- 신규 row 생성 설계 렌더링
- 생성 초안 입력/초기화
- 생성 preview/apply
- relation 후보 필터링
- 생성 lifecycle guide
- 삭제 dependency guard guide
- 생성→삭제→복원 일괄 점검
- 생성/삭제/복원 결과 요약 배너 helper
- create lifecycle split contract readiness 렌더링

## 유지한 안전장치

- dev key 필요
- 생성 확인 문구 필요: `CREATE MASTER DATA ROW`
- 생성 row 삭제 확인 문구 필요: `DELETE CREATED MASTER DATA ROW`
- 삭제 row 복원 확인 문구 필요: `RESTORE DELETED CREATED ROW`
- 일괄 점검 확인 문구 필요: `RUN CREATE DELETE RESTORE CHECK`
- 기존 preview guard 유지
- 기존 change log / rollback / create-delete / restore 흐름 유지

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상값:

```txt
v189.admin-create-lifecycle-split
```

```js
checkAdminReadOnlyPageReady().createLifecycleExternalReady
```

예상값:

```txt
true
```

```js
window.RpgAdminCreateLifecycle.VERSION
```

예상값:

```txt
v189.admin-create-lifecycle-split
```

## DB / env

- DB schema 변경 없음
- DB reset / seed 필요 없음
- `.env`, `.gitignore` 변경 없음
