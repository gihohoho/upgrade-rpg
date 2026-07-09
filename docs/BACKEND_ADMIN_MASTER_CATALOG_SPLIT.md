# Backend Admin Master Catalog Service Split

버전: **v200 backend admin master catalog/detail service split**

## 목적

`backend/app/services/admin_service.py`에서 마스터 데이터 카탈로그/상세/연결 조회 묶음을 외부 서비스 mixin으로 분리했습니다.

## 추가/변경 파일

- `backend/app/services/admin/admin_master_catalog_service.py`
- `tools/smoke_backend_admin_master_catalog_service_split.py`
- `backend/app/services/admin_service.py`
- `backend/app/services/admin_service_split_contract.py`
- `tools/run_smoke_core.sh`

## 분리된 기능

- `list_master_catalog_domains`
- `list_master_catalog_rows`
- `get_master_catalog_detail`
- `get_master_catalog_relations`
- master catalog/detail/relation helper
- relation edit option helper 일부
- read-only serializer/helper 일부

## 유지한 것

- `AdminService` facade 유지
- `backend/app/api/routes/admin.py` 변경 없음
- schema 변경 없음
- DB schema 변경 없음
- env 변경 없음
- 기존 API path/응답 구조 유지

## 확인

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v200.backend-admin-master-catalog-service-split
```

```js
checkAdminReadOnlyPageReady().backendMasterCatalogServiceSplitReady
```

예상:

```txt
true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
```

예상:

```txt
master-catalog-extracted-v200
```
