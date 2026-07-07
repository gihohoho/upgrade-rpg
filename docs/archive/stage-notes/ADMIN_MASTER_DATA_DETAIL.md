# v116 Admin Master Data Detail

## 목적

관리자 페이지에서 마스터 데이터 카탈로그의 행 하나를 선택해 상세 정보를 읽기 전용으로 확인한다.

이 단계는 편집/저장/삭제가 아니라, 이후 관리자 편집 화면을 만들기 전에 어떤 필드를 보여줄지 검증하는 단계다.

## 추가 API

```txt
GET /api/v1/admin/master-data/detail?domain=itemTemplates&id=1
```

응답은 다음 원칙을 지킨다.

```txt
readOnly=true
safeForAdminWriteUi=false
rawJsonReturned=false
assetsReturned=false
sanitizedJsonReturned=true
```

## 화면 기능

관리자 페이지의 `마스터 데이터 카탈로그` 표에 `보기` 버튼을 추가했다.

버튼을 누르면 아래 섹션에 표시된다.

```txt
선택한 마스터 데이터 상세
- 기본 필드
- 연결 요약
- 에셋 필드 숨김 상태
- JSON 안전 미리보기
```

## 안전장치

- DB를 수정하지 않는다.
- localStorage를 수정하지 않는다.
- 게임 런타임을 수정하지 않는다.
- 이미지 data URL은 내려주지 않는다.
- 긴 문자열/큰 JSON은 축약한다.
- JSON은 원본 통째로가 아니라 안전 미리보기로 표시한다.
- 관리자 쓰기 UI는 계속 차단 상태다.

## Console 확인

```js
// 위치: 브라우저 개발자도구 Console
await openAdminMasterDataDetail("itemTemplates", 1);
checkAdminReadOnlyPageReady();
```

## DB reset / seed

필요 없음.

기존 마스터 데이터 테이블을 조회만 한다.
