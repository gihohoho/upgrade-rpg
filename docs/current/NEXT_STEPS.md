# Next Steps — v371

## 현재 위치

- 공개 Render backend와 Static Site는 계속 v351로 Live입니다.
- v370 로그인·계정별 캐릭터 슬롯 8개·관리자 회원 관리 baseline은 로컬 검증 완료입니다.
- v371 필수 이메일 인증, 아이디 찾기, 비밀번호 재설정, 계정 삭제와 owner one-shot
  source가 준비됐습니다.
- local Alembic source graph head는 `v371_email_identity_lifecycle`입니다.
- local/live/Neon DB current는 `v295_initial_schema`이며 v371 upgrade·downgrade·stamp는
  0회입니다.
- backend/frontend v371 focused와 v370 회귀, migration parity, compileall/JavaScript,
  runtime blocking-I/O, route map 48 operations는 PASS입니다.
- `email-validator 2.3.0` 설치·Linux lock 갱신은 기호 승인 대기 중입니다.
- Brevo account/sender/API key·secret, 실제 메일, owner bootstrap, Render 배포는
  실행하지 않았습니다.

## 바로 다음 순서

1. 기호가 `email-validator 2.3.0` 설치·Linux lock 갱신을 승인합니다.
2. dependency와 lock, v371 migration source, 관련 source 검증을 마치고 준비 commit을
   push합니다.
3. 기호가 migration 적용 준비 commit의 정확한 40자리 SHA와 범위를 별도 검토합니다.
4. 승인 뒤에만 현재 DB `v295`, backup, v371 single head와 isolated migration
   roundtrip을 확인하고 local/Neon migration을 계획대로 한 번 적용합니다.
5. migration 완료 뒤 Brevo Free account, 인증된 sender, 프로젝트 전용 API key와
   `EMAIL_TOKEN_SECRET`·`PUBLIC_FRONTEND_ORIGIN` 설정을 별도로 확인합니다.
6. anonymous transactional tracking, log retention 1개월, email preview 미저장을
   확인한 뒤 테스트 메일 1건을 별도 승인합니다.
7. 새로운 exact-SHA 승인 뒤 owner one-shot bootstrap을 한 번 실행하고 plaintext
   password를 `.env`에서 즉시 제거합니다.
8. owner 이메일 인증·로그인과 두 캐릭터 이상의 저장 격리를 확인합니다.
9. rate limit, server session/refresh·원격 폐기, raw body cap, 다중 기기 revision,
   HTTPS/CSP/XSS와 개인정보·삭제 정책을 보강합니다.
10. 마지막에 backend image와 legacy static을 같은 exact-SHA release 단위로 준비합니다.

## 현재 승인에 포함되지 않는 것

- `email-validator` 승인 전 package 설치·lock 변경
- local/Neon DB write, migration apply·downgrade·stamp
- Brevo account·sender·API key·secret 생성 또는 실제 이메일 전송
- owner 관리자 bootstrap apply
- GitHub Actions·GHCR 게시, Render env 변경과 backend/static deploy
- 자동 migration, 자동 retry, custom domain/DNS와 결제
- 이번 요청 밖의 게임 콘텐츠·밸런스 변경

상세 계정 계약은 `ACCOUNT_EMAIL_VERIFICATION_RECOVERY_AND_DELETION.md`, DB head/current
구분과 migration 원칙은 `POSTGRES_ALEMBIC_READINESS.md`와
`POSTGRES_DEPLOYMENT_MIGRATION_RUNBOOK.md`를 봅니다.
