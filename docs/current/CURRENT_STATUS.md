# Current Status — v373

이 문서는 현재 구현과 승인 경계를 설명합니다. 장기 작업 규칙은 루트 [AGENTS.md](../../AGENTS.md), 새 채팅의 바로 다음 행동은 [NEXT_CHAT_HANDOFF.md](../../NEXT_CHAT_HANDOFF.md)가 기준입니다.

## 상태 표식

```txt
latest: v373.email-validator-linux-locks-obsidian-ready
strict result: email-validator-linux-locks-obsidian-ready
next safe stage: owner-review-v371-migration-source-and-approve-isolated-roundtrip
local Alembic source head: v371_email_identity_lifecycle
local/Neon DB current: v295_initial_schema
v371 apply/stamp/downgrade: 0/0/0
public backend/static: v351 Live
production approval/execution: no/no
```

## 현재 로컬 구현

- v372: 기능·DB·배포를 바꾸지 않고 Markdown 243개를 95개로 통합하고 `docs/current`의 실제 현재 문서를 11개로 줄였습니다. 문서 역할과 크기·중복·링크 smoke를 추가했습니다.
- v373: `email-validator==2.3.0` 설치와 Linux dependency lock/GHCR 재현성 해시 갱신, Obsidian 1.13.7 `Upgrade RPG` local vault 등록, 표준 Markdown 링크망과 작업 종료 문서 마감 규칙을 준비했습니다.
- v370: 회원가입·로그인, Bearer 인증, 계정별 캐릭터 슬롯 8개, 캐릭터별 local/DB 저장 격리, 관리자 회원 목록·상세·정지/해제와 감사 로그
- v371: 가입 이메일 필수화, 이메일 인증, 인증 재전송, 아이디 찾기, 비밀번호 재설정, 이메일 최종 확인을 거친 일반 회원 계정 삭제
- 비밀번호 재설정·계정 상태 변경은 `authVersion`을 올려 기존 access token을 무효화합니다.
- 이메일 action token 원문은 저장하지 않고 별도 `EMAIL_TOKEN_SECRET`의 HMAC-SHA256 digest만 저장합니다.
- 메일은 Render Free의 SMTP 제한 때문에 Brevo HTTPS API를 사용하도록 준비했으며 HTML과 plaintext 모두 게임 스타일 source-controlled template입니다.
- 계정 상단 UI는 크기를 키웠고 마을에서만 보입니다. 필드·보스·특수 구역에서는 hidden/inert입니다.
- owner 관리자는 app startup 자동 변경이 아니라 별도 one-shot 스크립트로만 만들 수 있습니다. exact SHA, clean tracked tree, 기존 관리자 0명, 명시 확인이 필요하고 이메일은 자동 인증하지 않습니다.

## DB와 의존성

- source graph에는 `v371_email_identity_lifecycle` revision이 있습니다.
- 실제 local/Neon DB는 계속 `v295_initial_schema`입니다. 이번 준비에서 migration apply·stamp·downgrade와 DB write를 하지 않았습니다.
- revision은 `users`에 legacy-safe nullable email identity, verification 시각, `auth_version`을 추가하고 `user_email_action_tokens`를 만듭니다.
- 검증된 이메일 정규화를 위한 `email-validator==2.3.0`과 전이 의존성 `dnspython==2.8.0`을 backend `.venv`와 Linux runtime/musllinux/dev lock에 반영했습니다. dependency가 빠지면 가입 관련 API는 계속 503으로 fail-closed합니다.
- 현재 생성 보고서는 [POSTGRES_ALEMBIC_READINESS.md](../generated/POSTGRES_ALEMBIC_READINESS.md)입니다. 상세 절차는 [migration runbook](../reference/database/POSTGRES_DEPLOYMENT_MIGRATION_RUNBOOK.md)에 있습니다.

## 검증 결과

- v373 Linux dependency lock `--check`, `pip check`, `email-validator 2.3.0` 정규화와 세 lock의 `email-validator`/`dnspython` exact pin 검사 PASS
- 설치 여부와 무관한 강제 import-failure 가입 `503`, v371 email/migration/owner와 v370 auth/admin focused 회귀 PASS
- 갱신된 5개 dependency/GHCR SHA의 strict·변조 fail-closed 공급망 검사 PASS
- v372 문서 구조 smoke: Markdown 95개, current 11개, exact duplicate 0, 활성 문서 broken link 0, 131개 stage-note 원본 경로 보존 PASS
- 문서 이동 뒤 generated report 4종 최신성, handoff readiness, frontend static plan, 전체 `tools/run_smoke_core.sh` PASS
- v371 이메일 lifecycle, migration source parity, owner bootstrap focused smoke PASS
- v370 auth/character/admin 회귀 PASS
- 인증 422 credential 비반사, SQL bind 숨김, action-token 단일 소비, IDOR·관리자 actor 재검증 PASS
- Python compileall, JavaScript syntax, runtime blocking-I/O, backend route map 48 operations PASS
- 실제 Chrome 기본 viewport와 `390×844`에서 계정 modal/account bar overflow 0, console warn/error 0
- 이메일 renderer는 외부 asset·web font·script 0, HTML escape와 plaintext fallback을 검사했습니다. 실제 메일 클라이언트 QA는 아직 하지 않았습니다.
- 독립 리뷰 기준 source-prepared 즉시 수정 blocker는 없습니다.

## 아직 실행하지 않은 것

- local/Neon v371 migration과 어떤 DB write도 없음
- Brevo 가입·발신자 확인·API key/secret 주입·실제 메일 발송
- owner bootstrap apply
- GitHub Actions, GHCR image 게시, Render env 변경과 backend/static 재배포
- custom domain, DNS, 결제

## 공개 전 필수 보강

현재 소스는 로컬 검토와 다음 승인 준비에는 적합하지만 공개 회원가입 배포에는 적합하지 않습니다.

1. IP·정규화 이메일별 rate limit과 반복 실패 지연
2. durable outbox/queue로 메일 발송 접수 시간 차이와 provider 지연 분리
3. ASGI raw request body cap
4. 만료된 미인증 계정 정리 또는 실제 메일 소유자의 안전한 계정 회수
5. 서버측 session/refresh/revoke와 로그인 상태 비밀번호 변경
6. 다중 기기 save revision/CAS와 충돌 해결
7. CSP/XSS, 개인정보 보관·삭제·감사 정책
8. Brevo tracking/log retention/preview 저장과 API key 회전 설정 검토

## 바로 다음 단계

1. v371 migration source와 dependency/lock 준비 결과를 검토합니다.
2. 별도 exact-SHA 승인 뒤 isolated PostgreSQL upgrade→downgrade→upgrade를 검증합니다.
3. migration apply, Brevo 설정, 테스트 메일, owner bootstrap, 공개 배포는 각각 다음 승인 단위로 분리합니다.

세부 인증 계약은 [이메일 인증·복구·삭제](ACCOUNT_EMAIL_VERIFICATION_RECOVERY_AND_DELETION.md), 기존 캐릭터 저장 계약은 [계정·캐릭터 슬롯](ACCOUNT_AUTH_AND_CHARACTER_SLOTS.md), 보안 후속은 [Security Gates](SECURITY_ROTATION_AND_GITHUB_GATES.md)를 봅니다.

## 배포와 기존 게임 상태

- 공개 frontend: `https://gihohoho-upgrade-rpg.onrender.com/index.html`, `/admin.html`
- 공개 backend: `https://upgrade-rpg-api.onrender.com`
- 공개 backend와 Static Site는 계속 v351입니다. v370/v371 로컬 계정 기능은 아직 배포하지 않았습니다.
- Neon PostgreSQL 16 Singapore는 v295 기준 22 application tables와 `alembic_version`을 유지합니다.
- GHCR namespace/repository는 `gihohoho` / `ghcr.io/gihohoho/upgrade-rpg-backend`입니다.
- 콘텐츠·장비 공식·이미지의 완료 이력은 `docs/reference/assets/`와 `docs/archive/history/`에서 찾습니다.
