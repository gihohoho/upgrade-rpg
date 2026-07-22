# Admin Edit Draft Shell

## 목적

관리자 페이지에서 마스터 데이터 항목을 선택했을 때, 실제 수정 기능을 붙이기 전에 어떤 필드가 편집 폼에 올라올지 미리 확인하는 잠금 UI입니다.

## 현재 상태

- 읽기 전용입니다.
- DB를 수정하지 않습니다.
- localStorage를 수정하지 않습니다.
- 게임 런타임을 수정하지 않습니다.
- 저장/되돌리기 버튼은 disabled 상태입니다.
- 원본 JSON과 이미지 data URL은 계속 숨깁니다.

## 확인 위치

```txt
관리자 페이지 → 마스터 데이터 카탈로그 → 보기 → 선택한 마스터 데이터 상세 → 관리자 편집 초안
```

## Console 확인

```js
// 위치: 브라우저 개발자도구 Console
getAdminEditDraftReadiness();
checkAdminReadOnlyPageReady();
```

## 다음 단계 후보

1. 수정 가능한 필드와 수정 금지 필드의 규칙을 백엔드 스키마로 분리
2. 변경 전/후 diff preview 추가
3. 관리자 쓰기 API를 만들되, 처음에는 `dryRun=true`만 허용
4. 실제 DB 반영은 관리자 인증과 감사 로그가 준비된 뒤 진행
