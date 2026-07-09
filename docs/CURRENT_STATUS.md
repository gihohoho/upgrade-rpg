# Current Status

현재 기준: **v192 admin master catalog/detail split**

이 패키지 기준 ZIP: **rpg_v192_admin_master_catalog_split_ready.zip**

## 완료된 관리자 JS 분리

- v185: layout shell 분리
- v187: change logs 분리
- v189.1: create lifecycle 분리 + helper export hotfix
- v191: edit draft 분리
- v192: master catalog/detail 분리

## v192 완료 내용

- `src/api/admin/admin-master-catalog.js` 추가
- master catalog filter/render/pagination 함수 이동
- master detail open/render 함수 이동
- master relations render/fetch 함수 이동
- master-data API verify/post-write verify 함수 이동
- `admin-page-readonly.js`에는 기존 함수명 wrapper 유지
- `admin.html` script 순서 갱신
- master catalog/detail split smoke 추가

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
checkAdminReadOnlyPageReady().masterCatalogExternalReady
window.RpgAdminMasterCatalog.VERSION
```

예상:

```txt
v192.admin-master-catalog-detail-split
true
v192.admin-master-catalog-detail-split
```

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음
