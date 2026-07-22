# Roadmap — v335

## 현재 위치

```txt
verified GHCR image: complete
isolated pull/runtime/cleanup: complete
production deploy plan review: complete
cost-minimum provider selection: Render Free + Neon Free Singapore
account onboarding/resources: unresolved/not created
deployment approval/execution: no/no
```

v335 strict result는 `cost-minimum-production-provider-selected-account-onboarding-required`, 다음 단계는 `owner-connect-render-and-neon-accounts`입니다. v334 실행 안전 baseline은 `production-deploy-plan-reviewed-inputs-blocked`, 역사 next-stage marker는 `select-production-targets-and-complete-executable-deploy-plan`로 유지합니다.

## 다음 순서

1. 기호가 Render Hobby와 Neon Free에 로그인합니다. Render 결제수단은 추가하지 않습니다.
2. Render Free Web Service와 Neon Free PostgreSQL 16을 Singapore에 만들기 직전 설정을 검토합니다.
3. resource 생성 범위와 DB 초기화/이식 범위를 분리해 승인합니다.
4. 실제 endpoint를 Git 밖 Render secret에 넣고 `verify-full` certificate path를 live 확인합니다.
5. Render `onrender.com` HTTPS origin을 CORS에 고정하고 health check를 준비합니다.
6. Codex가 placeholder 없는 실행 준비 계획을 만들고 정적 검증합니다.
7. 기호가 그 준비 commit의 정확한 40자리 SHA를 한 번 승인합니다.
8. 승인 범위에서만 실제 deploy하고 sanitized evidence를 기록합니다.

DB/Alembic mutation, volume 삭제, 자동 deploy/retry는 이 순서에 포함하지 않습니다. 코드나 image 포함 콘텐츠가 바뀌면 현재 digest를 재사용하지 않고 새 공급망 검증부터 진행합니다.
