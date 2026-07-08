# Admin Create Lifecycle Split Contract

현재 버전: **v188 admin create lifecycle split contract**

## 목적

`create lifecycle` 기능을 실제 외부 JS 파일로 분리하기 전에, 필요한 API 함수, window export, DOM target, 확인 문구, delegated action을 먼저 고정합니다.

이번 단계에서는 실제 파일 분리를 하지 않습니다.

다음 후보 파일명은 아래로 고정합니다.

```txt
src/api/admin/admin-create-lifecycle.js
```

## 계약 상태

```txt
contract-frozen-v188
```

## 현재 파일

```txt
src/api/admin-page-readonly.js
```

## 다음 분리 후보 파일

```txt
src/api/admin/admin-create-lifecycle.js
```

## 고정한 범위

- 생성 설계 필터
- 생성 설계 렌더링
- 생성 초안 입력값 읽기
- 생성 preview/apply
- 생성 lifecycle 가이드 렌더링
- 삭제 dependency guard 표시
- 생성→삭제→복원 일괄 점검
- 생성/삭제/복원 확인 문구
- 동적 DOM target 목록
- delegated action 목록

## 대표 확인 문구

```txt
CREATE MASTER DATA ROW
DELETE CREATED MASTER DATA ROW
RESTORE DELETED CREATED ROW
RUN CREATE DELETE RESTORE CHECK
```

## 브라우저 확인

관리자 페이지 Console에서 아래를 실행합니다.

```js
checkAdminReadOnlyPageReady().createLifecycleSplitContractReady
```

예상값:

```txt
true
```

상세 진단은 아래로 확인합니다.

```js
getAdminCreateLifecycleSplitContractReadiness()
```

## smoke

실행 위치: 프로젝트 루트

```bash
node tools/smoke_admin_create_lifecycle_split_contract.js
```

core smoke에도 포함했습니다.

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```

## DB reset / seed

- DB schema 변경 없음.
- DB reset 필요 없음.
- seed 재실행 필요 없음.
- `.env`, `.gitignore` 변경 없음.
