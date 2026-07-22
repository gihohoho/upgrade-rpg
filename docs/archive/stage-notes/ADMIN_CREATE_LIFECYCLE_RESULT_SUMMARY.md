# Admin Create Lifecycle Result Summary

## 목적

v182는 신규 row 생성 기능을 더 여는 단계가 아니라, 이미 열린 생성→삭제→복원 흐름의 결과 화면을 더 안전하게 읽기 위한 관리자 UI 보강 단계입니다.

삭제/복원 preview 결과에서 중요한 차단 사유를 작은 pill만으로 보지 않고, 상단 요약 카드에서 바로 확인할 수 있게 했습니다.

## 변경 내용

### 생성 row 삭제 결과 요약

`create` 이력 상세에서 `생성 row 삭제 미리보기`를 누르면 결과 상단에 큰 요약 카드가 표시됩니다.

표시 항목:

- 현재값 불일치 수
- 연결 검사 수
- 차단 guard 수
- 차단 row 수
- dryRun 상태

백엔드 응답에도 아래 보조 count를 추가했습니다.

- `dependencyCheckCount`
- `dependencyBlockerGuardCount`
- 기존 `dependencyBlockerCount` 유지

`dependencyBlockerCount`는 실제 연결 row 개수 합계입니다. `dependencyBlockerGuardCount`는 차단된 검사 항목 개수입니다.

### 삭제 row 복원 결과 요약

`create_delete` 이력 상세에서 `삭제 row 복원 미리보기`를 누르면 결과 상단에 큰 요약 카드가 표시됩니다.

표시 항목:

- 충돌/오류 합계
- 검증 오류 수
- relation 값 수
- id 충돌 여부
- code 충돌 여부

백엔드 응답에도 아래 보조 count를 추가했습니다.

- `restoreConflictCount`

`restoreConflictCount`는 id 충돌, code 충돌, validation error를 합산한 값입니다.

## 안정성

- 새 쓰기 도메인 오픈 없음.
- 삭제/복원 적용 조건 변경 없음.
- 기존 dev key, 확인 문구, preview 안전검사 유지.
- 기존 `dependencyChecks`, `validationErrors` 상세 테이블 유지.
- UI 요약과 count 필드만 추가.

## 확인 방법

브라우저에서 관리자 페이지를 열고 아래 순서로 확인합니다.

1. 변경 이력에서 `create` 이력을 엽니다.
2. `생성 row 삭제 미리보기`를 누릅니다.
3. 결과 상단에 `생성 row 삭제 가능` 또는 `생성 row 삭제 차단` 요약 카드가 보이는지 확인합니다.
4. 변경 이력에서 `create_delete` 이력을 엽니다.
5. `삭제 row 복원 미리보기`를 누릅니다.
6. 결과 상단에 `삭제 row 복원 가능` 또는 `삭제 row 복원 차단` 요약 카드가 보이는지 확인합니다.

브라우저 Console 확인:

```js
checkAdminReadOnlyPageReady().version
```

예상값:

```txt
v182.admin-create-lifecycle-result-summary
```

추가 확인:

```js
checkAdminReadOnlyPageReady().createLifecycleResultSummaryReady
```

예상값:

```txt
true
```

## DB reset / seed

필요 없음.

- DB schema 변경 없음.
- seed 변경 없음.
- `.env`, `.gitignore` 변경 없음.
