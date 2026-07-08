# Admin Create Delete Restore

## 목적

v168에서 `create` 이력으로 생성한 row를 안전 검사 후 삭제할 수 있게 열었다.
v169~v171에서는 그 다음 단계로, `create_delete` 이력으로 삭제한 row를 다시 복원하는 preview/apply 흐름을 제한적으로 추가했다.

## 추가된 API

- `POST /api/v1/admin/change-logs/{change_log_id}/create-delete-restore-preview`
- `POST /api/v1/admin/change-logs/{change_log_id}/create-delete-restore-apply`

## 복원 가능 조건

복원은 아래 조건을 모두 만족해야 한다.

- change log action이 `create_delete`여야 한다.
- 대상 도메인이 제한 allow-list에 있어야 한다.
  - `characters`
  - `enhancementGroups`
  - `fieldZones`
- 삭제된 row의 원래 id가 현재 DB에 없어야 한다.
- 삭제된 row의 원래 code가 다른 row에서 재사용되지 않아야 한다.
- 저장된 삭제 전 값이 생성 blueprint 검증을 다시 통과해야 한다.

## 충돌 검사

preview 응답은 아래 값을 내려준다.

- `idConflict`
- `codeConflict`
- `targetRowMissing`
- `validationErrorCount`
- `createDeleteRestoreReady`

충돌이나 검증 오류가 있으면 실제 복원 apply는 차단된다.

## 확인 문구

실제 복원 apply에는 dev key와 아래 확인 문구가 필요하다.

```txt
RESTORE DELETED CREATED ROW
```

## change log

복원 성공 시 `admin_change_logs`에 아래 action을 남긴다.

```txt
action=create_delete_restore
```

## 아직 잠근 부분

`create_delete_restore` 이력으로 복원한 row를 다시 자동 삭제하는 별도 re-delete 흐름은 아직 열지 않았다.
필요하면 다음 단계에서 preview부터 설계한다.

## DB reset / seed

DB reset / seed 필요 없음.
DB schema 변경 없음.
