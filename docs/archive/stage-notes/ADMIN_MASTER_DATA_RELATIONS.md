# v117 Admin Master Data Relations

## 목적

관리자 페이지의 마스터 데이터 상세 화면에서, 선택한 행과 연결된 다른 마스터 데이터를 읽기 전용으로 바로 확인한다.

이 단계는 편집/저장/삭제가 아니라, 관리자 편집 화면으로 가기 전에 데이터 관계를 눈으로 확인하는 단계다.

## 추가 API

```txt
GET /api/v1/admin/master-data/relations?domain=itemTemplates&id=1&limit=20
```

응답은 다음 원칙을 지킨다.

```txt
readOnly=true
safeForAdminWriteUi=false
rawJsonReturned=false
assetsReturned=false
```

## 연결 항목 예시

```txt
아이템 템플릿 → 드랍 아이템 / 강화 그룹 / 강화 단계
스킬 → 스킬 레벨 / 캐릭터 스킬 연결
보스 → 보스 드랍 테이블
필드 → 필드 드랍 테이블
드랍 테이블 → 대상 보스/필드 / 드랍 아이템
강화 그룹 → 강화 단계 / 연결 아이템
```

## 화면 기능

`마스터 데이터 카탈로그 → 보기`를 누르면 상세 화면에 다음 영역이 함께 표시된다.

```txt
실제 연결 항목
```

연결 항목 표에서도 `보기` 버튼을 누르면 해당 관련 마스터 데이터의 상세로 이동한다.

## 안전장치

- DB를 수정하지 않는다.
- localStorage를 수정하지 않는다.
- 게임 런타임을 수정하지 않는다.
- 원본 JSON 통째로 내려주지 않는다.
- 이미지 data URL을 내려주지 않는다.
- 관련 행은 카탈로그와 같은 축약된 cells만 표시한다.
- 관리자 쓰기 UI는 계속 차단 상태다.

## Console 확인

```js
// 위치: 브라우저 개발자도구 Console
await openAdminMasterDataDetail("itemTemplates", 1);
await openAdminMasterDataRelations("itemTemplates", 1);
checkAdminReadOnlyPageReady();
```

## DB reset / seed

필요 없음.

기존 마스터 데이터 테이블을 조회만 한다.
