# Roadmap — v334

## 현재 위치

```txt
verified GHCR image: complete
isolated pull/runtime/cleanup: complete
production deploy plan review: complete
required production inputs: unresolved
deployment approval/execution: no/no
```

strict result는 `production-deploy-plan-reviewed-inputs-blocked`, 다음 단계는 `select-production-targets-and-complete-executable-deploy-plan`입니다.

## 다음 순서

1. production host/provider/region/OS/access를 선택합니다.
2. managed PostgreSQL provider/product/region/network와 provider CA를 선택합니다.
3. reverse proxy 또는 ingress, domain, DNS, certificate 책임을 선택합니다.
4. Git 밖의 secret injection과 external edge network를 정합니다.
5. managed DB backup과 first-deploy rollback 담당을 확인합니다.
6. Codex가 placeholder 없는 실행 준비 계획을 만들고 정적 검증합니다.
7. 기호가 그 준비 commit의 정확한 40자리 SHA를 한 번 승인합니다.
8. 승인 범위에서만 실제 deploy하고 sanitized evidence를 기록합니다.

DB/Alembic mutation, volume 삭제, 자동 deploy/retry는 이 순서에 포함하지 않습니다. 코드나 image 포함 콘텐츠가 바뀌면 현재 digest를 재사용하지 않고 새 공급망 검증부터 진행합니다.
