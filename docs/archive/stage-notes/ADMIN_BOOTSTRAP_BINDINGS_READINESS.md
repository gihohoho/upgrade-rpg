# v194 Admin Bootstrap / bindEvents Readiness

## 목적

v194는 `admin-page-readonly.js`를 바로 더 쪼개기 전에, 마지막 entry 파일에 남아 있는 bootstrap / bindEvents / window export 역할을 계약으로 고정한 단계입니다.

실제 새 파일 분리는 하지 않았습니다.

## 고정한 항목

- boot 순서
- delegated event action map
- window export 호환 목록
- 외부 모듈 configure 순서
- readiness aggregation 진단

## 새 readiness

브라우저 Console에서 아래 값으로 확인할 수 있습니다.

```js
checkAdminReadOnlyPageReady().bootstrapBindingReady
```

예상값:

```txt
true
```

상세 확인:

```js
getAdminBootstrapBindingReadiness()
```

예상 status:

```txt
contract-frozen-v194
```

## 새 smoke

실행 위치: 프로젝트 루트

```bash
node tools/smoke/frontend/smoke_admin_bootstrap_bindings_readiness.js
```

core smoke에도 포함했습니다.

## DB / env

- DB schema 변경 없음
- seed 변경 없음
- API route 변경 없음
- `.env` 변경 없음
- DB reset 필요 없음
