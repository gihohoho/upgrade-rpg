# NEXT CHAT HANDOFF — v192

기호는 코딩/터미널/경로에 익숙하지 않으므로, 명령어는 항상 실행 위치를 먼저 적습니다.

## 현재 안정 버전

**v192 admin master catalog/detail split**

## 현재 ZIP

**rpg_v192_admin_master_catalog_split_ready.zip**

## v192 완료

- `src/api/admin/admin-master-catalog.js` 추가
- master catalog/detail 실제 분리 1단계 완료
- 카탈로그 필터/렌더/페이지네이션/선택 row 표시 분리
- 마스터 상세/relations/API verify/post-write verify 분리
- 기존 window 함수명은 `admin-page-readonly.js` wrapper로 유지
- `admin.html` script 순서에 master catalog 파일 추가
- `tools/smoke_admin_master_catalog_split.js` 추가
- core smoke 통과

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v192.admin-master-catalog-detail-split
```

```js
checkAdminReadOnlyPageReady().masterCatalogExternalReady
```

예상:

```txt
true
```

```js
window.RpgAdminMasterCatalog.VERSION
```

예상:

```txt
v192.admin-master-catalog-detail-split
```

## 다음 추천 단계

v193은 **admin overview/snapshot 분리**를 추천합니다.

후보 파일:

```txt
src/api/admin/admin-overview-snapshots.js
```

추천 범위:

- overview cards 렌더링
- master count summary table 렌더링은 이미 master module로 이동됨
- save snapshot 필터 read/reset/describe
- save snapshot table 렌더링

이 부분은 DB 쓰기와 직접 관련이 없어서 실제 분리로 바로 가도 비교적 안전합니다.

## 주의

v192에서 master detail/API verify 쪽을 실제 분리했으므로, 브라우저에서 상세 보기, 연결 항목 불러오기, 선택 항목 API 반영 확인 버튼을 한 번씩 눌러 확인하는 것을 권장합니다.
