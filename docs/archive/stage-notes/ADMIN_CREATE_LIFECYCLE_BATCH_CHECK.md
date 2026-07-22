# Admin Create Lifecycle Batch Check

v183은 이미 열린 신규 row 생성·삭제·복원 흐름을 브라우저에서 한 번에 점검할 수 있게 하는 관리자 UI 보강 단계입니다.

## 목적

기존에는 아래 순서를 손으로 하나씩 눌러야 했습니다.

1. 생성 초안 검증
2. 실제 생성 적용
3. `create` 변경 이력 열기
4. 생성 row 삭제 미리보기
5. 생성 row 삭제 적용
6. `create_delete` 변경 이력 열기
7. 삭제 row 복원 미리보기
8. 삭제 row 복원 적용

v183에서는 현재 생성 초안을 기준으로 이 흐름을 일괄 실행하는 버튼을 추가했습니다.

## 새 UI

관리자 페이지의 `신규 row 생성·삭제·복원 점검` 섹션에 아래 카드가 추가됩니다.

- 생성→삭제→복원 일괄 점검
- 일괄 점검 사유 입력
- 일괄 점검 확인 문구 입력
- 생성→삭제→복원 한 번에 점검 버튼
- 단계별 결과 테이블

## 일괄 점검 확인 문구

아래 문구를 정확히 입력해야 실행됩니다.

```txt
RUN CREATE DELETE RESTORE CHECK
```

## 실행되는 단계

일괄 점검 버튼은 아래 순서를 그대로 실행합니다.

1. 생성 preview
2. 생성 apply
3. 삭제 preview
4. 삭제 apply
5. 복원 preview
6. 복원 apply

각 단계는 기존 백엔드 안전검사를 그대로 사용합니다.

## 안전장치

- 관리자 dev key가 저장되어 있어야 합니다.
- 생성 초안의 `생성 확인 문구`에 `CREATE MASTER DATA ROW`가 입력되어 있어야 합니다.
- 일괄 점검 확인 문구에 `RUN CREATE DELETE RESTORE CHECK`가 입력되어 있어야 합니다.
- 브라우저 confirm 창에서 한 번 더 확인해야 합니다.
- 생성/delete/restore apply는 모두 기존 FastAPI guarded write API를 사용합니다.
- 삭제 preview에서 dependency blocker가 있으면 삭제 apply로 넘어가지 않습니다.
- 복원 preview에서 id/code 충돌이나 validation error가 있으면 복원 apply로 넘어가지 않습니다.

## 주의

일괄 점검이 성공하면 마지막 단계에서 row가 다시 복원됩니다.
따라서 테스트 row는 DB에 남습니다.
필요 없으면 `create` 이력에서 다시 생성 row 삭제를 실행하면 됩니다.

## readiness

브라우저 개발자도구 Console에서 아래 값이 `true`면 정상입니다.

```js
checkAdminReadOnlyPageReady().createLifecycleBatchCheckReady
```

버전 확인값은 아래와 같습니다.

```txt
v183.admin-create-lifecycle-batch-check
```

## DB reset / seed

- DB schema 변경 없음.
- DB reset 필요 없음.
- seed 재실행 필요 없음.
- `.env`, `.gitignore` 변경 없음.
