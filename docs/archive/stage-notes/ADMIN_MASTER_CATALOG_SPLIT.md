# Admin Master Catalog/Detail Split

버전: **v192 admin master catalog/detail split**

## 목적

관리자 페이지의 마스터 데이터 카탈로그/상세/연결 항목/API 반영 확인 로직을 `admin-page-readonly.js`에서 분리해, 이후 관리자 화면을 Vue/FastAPI 관리자 구조로 옮기기 쉽게 만드는 단계입니다.

## 새 파일

```txt
src/api/admin/admin-master-catalog.js
```

## 분리한 기능

- 마스터 카탈로그 필터 읽기/초기화/설명
- 도메인 select 동기화
- 마스터 데이터 요약 테이블 렌더링
- 카탈로그 테이블 렌더링
- 페이지네이션 렌더링
- 선택 row 표시
- 상세 열기
- code 기반 relation 대상 열기
- 실제 연결 항목 렌더링/조회
- `/game/master-data` API 반영 확인
- DB write 이후 자동 API 반영 확인

## 유지한 것

`admin-page-readonly.js`에는 기존 window 함수명을 유지하는 thin wrapper를 남겼습니다.

예:

```txt
openAdminMasterDataDetail
openAdminMasterDataDetailByCode
openAdminMasterDataRelations
verifySelectedMasterDataApi
runPostWriteMasterApiVerification
```

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

## 검증

```bash
bash tools/run_smoke_core.sh
```

```bash
node --check src/api/admin/admin-master-catalog.js
node --check src/api/admin-page-readonly.js
```

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음
