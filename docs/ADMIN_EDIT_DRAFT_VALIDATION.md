# Admin Edit Draft Validation

v119 단계에서는 관리자 페이지의 `관리자 편집 초안`을 한 단계 진전시켰다.

기존 v118은 입력칸이 모두 disabled인 잠금 폼이었다. v119부터는 관리자가 값을 직접 바꿔볼 수 있고, `초안 검증` 버튼으로 FastAPI에 dry-run 검증을 요청할 수 있다.

## 추가 API

```txt
POST /api/v1/admin/master-data/edit-preview
```

요청 예시:

```json
{
  "domain": "itemTemplates",
  "id": 1,
  "draft": {
    "name": "수정 테스트 이름",
    "stackable": true
  },
  "dryRun": true
}
```

## 안전장치

- DB를 수정하지 않는다.
- `session.commit()`을 호출하지 않는다.
- 모델 속성에 값을 대입하지 않는다.
- 원본 JSON과 이미지 data URL을 반환하지 않는다.
- `id`, `created_at`, `updated_at` 같은 시스템 필드는 수정 불가로 검증한다.
- `_json` 필드와 asset 필드는 아직 편집 대상에서 제외한다.
- 실제 `변경 저장` 버튼은 계속 disabled 상태다.

## 프론트 Console 헬퍼

```js
// 위치: 브라우저 개발자도구 Console
readAdminEditDraftValues();
await previewAdminEditDraft();
resetAdminEditDraft();
getAdminEditDraftReadiness();
```

## 다음 단계 후보

- 변경 이력 테이블 설계
- 변경 적용 전 확인 모달
- admin 권한 정책 연결
- rollback/snapshot 정책 설계
- 이후에야 실제 저장 API 개방
