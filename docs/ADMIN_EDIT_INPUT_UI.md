# Admin Edit Input UI

v133에서는 관리자 편집 초안의 입력 UI를 필드 타입에 맞게 더 명확하게 바꿨습니다.

## 변경 내용

- boolean 필드는 checkbox 대신 `true / false` select로 표시합니다.
  - 예: `stackable`, `is_enabled`, `is_default`
- number 필드는 `type="number"` 입력칸으로 표시합니다.
  - 예: `hp`, `grade`, `proc_rate`, `cooldown_seconds`, `rate`, `gold_cost`
- `description`, `admin_note`는 항상 textarea로 표시합니다.
- allow-list 밖 필드는 입력칸을 만들지 않고, `읽기 전용/잠금 필드` 카드로 따로 보여줍니다.
- 잠금 사유를 같이 표시합니다.
  - 식별자 필드
  - 관계/연결 필드
  - JSON 원본 필드
  - 자동 시간 필드
  - allow-list 밖 필드

## 안전 원칙

- 백엔드 API, DB schema, seed 데이터는 변경하지 않았습니다.
- localStorage 저장 구조도 변경하지 않았습니다.
- 기존 guarded apply, dev key guard, 확인 문구, stale guard는 그대로 유지합니다.
- 입력 UI만 바꾼 단계라 DB reset / seed는 필요 없습니다.

## 브라우저 확인

```js
// 위치: 브라우저 개발자도구 Console
checkAdminReadOnlyPageReady();
```

```js
// 위치: 브라우저 개발자도구 Console
getAdminDraftFieldInputKind({ key: "stackable", value: true });
```

예상 결과:

```txt
boolean-select
```

```js
// 위치: 브라우저 개발자도구 Console
getAdminDraftFieldInputKind({ key: "hp", value: 1000 });
```

예상 결과:

```txt
number
```
