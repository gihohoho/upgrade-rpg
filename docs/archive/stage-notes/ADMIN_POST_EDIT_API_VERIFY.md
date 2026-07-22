# Admin Post-edit API Verify

v128에서 관리자 마스터 데이터 **실제 적용/되돌리기 후 자동 master-data API 확인**을 추가했습니다.

## 목적

v127에서는 관리자가 직접 `선택 항목 API 반영 확인` 버튼을 눌러야 했습니다.

v128부터는 아래 작업이 성공하면 관리자 페이지가 자동으로 상세를 다시 불러오고 `/api/v1/game/master-data` 응답까지 확인합니다.

```txt
DB 적용 성공
→ 상세 다시 불러오기
→ /game/master-data 자동 조회
→ 관리자 상세 값과 API 값 비교
→ 게임 새로고침 필요 안내
```

## DB 적용 후 자동 확인

관리자 편집 초안에서 확인 문구 `APPLY MASTER DATA EDIT`를 입력하고 실제 적용이 성공하면 자동으로 실행됩니다.

```txt
관리자 편집 초안
→ 검사 후 실제 적용
→ DB 적용 완료
→ 선택 항목 상세 자동 재조회
→ master-data API 자동 비교
```

## 되돌리기 후 자동 확인

변경 이력에서 확인 문구 `ROLLBACK MASTER DATA EDIT`를 입력하고 되돌리기가 성공하면 자동으로 실행됩니다.

```txt
관리자 변경 이력
→ 검사 후 되돌리기
→ DB 되돌리기 완료
→ 되돌린 대상 상세 자동 재조회
→ master-data API 자동 비교
```

## 중요한 점

이 기능은 자동 확인만 수행합니다.

- DB는 이미 guarded apply/rollback 단계에서만 변경됩니다.
- 이 기능 자체는 추가 DB 수정을 하지 않습니다.
- localStorage를 수정하지 않습니다.
- 현재 켜져 있는 게임 런타임 객체를 직접 바꾸지 않습니다.
- 인게임 반영은 여전히 게임 새로고침 후 적용됩니다.

## Console helper

```js
// 위치: 브라우저 개발자도구 Console
await verifySelectedMasterDataApi();

// 보통 직접 쓸 일은 없지만 자동 확인 헬퍼도 노출되어 있습니다.
await runPostWriteMasterApiVerification("bosses", 1, { label: "수동 확인" });
```

## DB reset / seed

필요 없습니다.
