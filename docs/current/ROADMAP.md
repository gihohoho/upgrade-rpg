# Roadmap — v337

## 현재 위치

```txt
verified GHCR image: complete
isolated pull/runtime/cleanup: complete
production deploy plan review: complete
cost-minimum provider selection: Render Free + Neon Free Singapore
Neon project/read-only connectivity: created/verified
Render account/plan/payment: connected/Hobby (legacy)/no card
Render registry credential/resource: absent/not created
deployment approval/execution: no/no
```

v337 strict result는 `render-hobby-no-card-existing-image-private-ghcr-credential-required`, 다음 단계는 `owner-complete-github-confirm-access-then-resume-approved-render-credential-flow`입니다. v336 Neon 연결 증거, v335 공급자 선택, v334 실행 안전 baseline은 계속 보존합니다.

## 다음 순서

1. 기호가 GitHub `Confirm access` verification code 입력과 `Verify`를 완료합니다. credential 범위 승인은 이미 완료됐습니다.
2. token을 노출하지 않고 dedicated classic PAT와 Render registry credential을 만들고 private GHCR pull 접근만 확인합니다.
3. Render Free image-backed Web Service Singapore 생성 직전 설정을 검토합니다.
4. 현재 `neondb`와 계획상 `rpg_game` 차이를 포함한 DB 생성·초기화·이식 계획을 별도로 검토합니다.
5. resource 생성 범위와 DB 초기화/이식 범위를 분리해 승인합니다.
6. actual URL은 Git 밖 Render secret에 넣고 `verify-full` 동등 TLS 설정을 live 확인합니다.
7. Render `onrender.com` HTTPS origin을 CORS에 고정하고 health check를 준비합니다.
8. Codex가 placeholder 없는 실행 준비 계획을 만들고 정적 검증합니다.
9. 기호가 그 준비 commit의 정확한 40자리 SHA를 한 번 승인합니다.
10. 승인 범위에서만 실제 deploy하고 sanitized evidence를 기록합니다.

DB/Alembic mutation, volume 삭제, 자동 deploy/retry는 이 순서에 포함하지 않습니다. 코드나 image 포함 콘텐츠가 바뀌면 현재 digest를 재사용하지 않고 새 공급망 검증부터 진행합니다.
