# v105 Save Data Preview / Compare

백엔드 DB에 저장된 세이브를 실제 게임에 덮어쓰기 전에, 현재 브라우저 localStorage 세이브와 DB 세이브를 비교하는 안전 점검 단계입니다.

## 목적

아직 DB 세이브를 게임에 자동 적용하지 않습니다.

이 단계에서는 다음만 확인합니다.

- 현재 브라우저 localStorage 세이브 존재 여부
- 백엔드 DB 세이브 존재 여부
- 레벨, 골드, 필드, 인벤토리 수, 창고 수, 우편 수, 장착 슬롯 수 차이
- 원본 JSON 스냅샷이 완전히 같은지 여부

## 브라우저 Console 함수

```js
await previewBackendSaveSnapshot();
```

결과 객체의 주요 필드:

- `local`: 현재 브라우저 저장 요약
- `backend`: DB 저장 요약
- `comparison.diffCount`: 주요 항목 차이 개수
- `comparison.sameRawSnapshot`: 원본 JSON까지 완전히 같은지 여부
- `recommendation`: 다음 행동 추천

## recommendation 의미

- `same_snapshot_safe`: localStorage와 DB 저장값이 완전히 같음
- `backend_empty_push_local_first`: DB에 저장값이 없으므로 먼저 수동 저장 또는 `sync DB` 필요
- `different_review_before_restore`: localStorage와 DB 값이 다르므로 복구 전에 반드시 확인 필요
- `minor_or_hidden_difference_review_raw`: 주요 요약은 같지만 원본 JSON에 차이가 있음
- `local_missing`: 브라우저 localStorage 저장값이 없음

## 주의

이 기능은 비교 전용입니다. DB 세이브를 게임에 적용하거나 localStorage를 덮어쓰지 않습니다.
