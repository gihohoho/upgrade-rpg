# Admin Write Dev Key Guard

버전: v130

## 목적

관리자 페이지에서 실제 DB를 수정하는 기능이 열렸기 때문에, 운영 로그인/RBAC를 붙이기 전까지 임시로 로컬 개발용 쓰기 잠금장치를 둔다.

## 핵심 흐름

읽기 API와 미리보기 API는 그대로 사용할 수 있다.

쓰기 API는 `X-Admin-Dev-Key` 헤더가 있어야만 통과한다.

대상 API:

- `POST /api/v1/admin/master-data/edit-apply`
- `POST /api/v1/admin/change-logs/{change_log_id}/rollback-apply`

계속 dev key가 필요 없는 API:

- overview
- catalog/detail/relations
- edit-preview
- rollback-preview
- change log list/detail
- save snapshot list

## 기본 로컬 키

로컬 기본값은 아래와 같다.

```txt
local-admin-dev-key
```

`.env`에서 바꾸려면:

```env
ADMIN_WRITE_DEV_KEY="원하는-로컬-dev-key"
```

## 관리자 페이지 사용법

관리자 페이지의 `관리자 쓰기 dev key 잠금` 영역에서 dev key를 입력하고 저장한다.

이 값은 `sessionStorage`에 저장된다.
브라우저 탭 단위 임시 저장이므로, 탭을 닫으면 다시 입력해야 할 수 있다.

## 안전장치

이 기능은 실제 보안 인증이 아니다.
운영 배포 전에는 반드시 로그인, 세션/JWT, 관리자 권한 검증, CSRF/권한 로그 정책으로 대체해야 한다.

현재 목적은 로컬 개발 중 실수로 관리자 쓰기 API를 호출하는 일을 줄이는 것이다.

## DB reset / seed 필요 여부

필요 없음.

DB 구조 변경 없이 백엔드 설정, 헤더 검사, 프론트 관리자 페이지 입력 UI만 추가했다.
