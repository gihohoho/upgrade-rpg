# Roadmap — v336

## 현재 위치

```txt
verified GHCR image: complete
isolated pull/runtime/cleanup: complete
production deploy plan review: complete
cost-minimum provider selection: Render Free + Neon Free Singapore
Neon project/read-only connectivity: created/verified
Render onboarding/resource: unresolved/not created
deployment approval/execution: no/no
```

v336 strict result는 `neon-direct-pooled-readonly-connectivity-verified`, 다음 단계는 `owner-connect-render-and-review-database-initialization-plan`입니다. v335 공급자 선택과 v334 실행 안전 baseline은 계속 보존합니다.

## 다음 순서

1. 기호가 Render Hobby에 로그인합니다. Render 결제수단은 추가하지 않습니다.
2. Render Free image-backed Web Service Singapore 생성 직전 설정을 검토합니다.
3. 현재 `neondb`와 계획상 `rpg_game` 차이를 포함한 DB 생성·초기화·이식 계획을 별도로 검토합니다.
4. resource 생성 범위와 DB 초기화/이식 범위를 분리해 승인합니다.
5. actual URL은 Git 밖 Render secret에 넣고 `verify-full` 동등 TLS 설정을 live 확인합니다.
6. Render `onrender.com` HTTPS origin을 CORS에 고정하고 health check를 준비합니다.
7. Codex가 placeholder 없는 실행 준비 계획을 만들고 정적 검증합니다.
8. 기호가 그 준비 commit의 정확한 40자리 SHA를 한 번 승인합니다.
9. 승인 범위에서만 실제 deploy하고 sanitized evidence를 기록합니다.

DB/Alembic mutation, volume 삭제, 자동 deploy/retry는 이 순서에 포함하지 않습니다. 코드나 image 포함 콘텐츠가 바뀌면 현재 digest를 재사용하지 않고 새 공급망 검증부터 진행합니다.
