# Admin Catalog Selection Helper

현재 기준: **v138 admin safe apply review**

마스터 데이터 카탈로그에서 어떤 행의 상세를 보고 있는지 더 쉽게 확인할 수 있도록 선택 행 표시를 추가했습니다.

## 변경 내용

- 카탈로그 행의 `보기` 버튼을 누르면 해당 행이 강조됩니다.
- 선택된 행에는 `선택됨` 배지가 표시됩니다.
- 페이지를 다시 렌더링해도 현재 상세 대상이 현재 페이지에 있으면 선택 표시가 다시 붙습니다.
- 이 기능은 관리자 UI 표시만 바꾸며 DB/localStorage/game runtime은 수정하지 않습니다.

## 확인용 Console helper

```txt
markSelectedMasterCatalogRow(domain, id)
```

예시:

```txt
markSelectedMasterCatalogRow("itemTemplates", 1)
```

## DB 영향

DB reset / seed는 필요 없습니다.
