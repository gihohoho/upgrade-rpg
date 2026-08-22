# Current Status — v377

이 문서는 현재 구현과 승인 경계를 설명합니다. 장기 작업 규칙은 루트 [AGENTS.md](../../AGENTS.md), 새 채팅의 바로 다음 행동은 [NEXT_CHAT_HANDOFF.md](../../NEXT_CHAT_HANDOFF.md)가 기준입니다.

## 상태 표식

```txt
latest: v377.local-email-auth-unblocked
strict result: local-email-auth-unblocked
next safe stage: configure-v377-local-brevo-provider
local Alembic source head: v377_auth_email_public_security
local/Neon DB current: v377_auth_email_public_security / v295_initial_schema
v377 apply/stamp/downgrade: local 1/0/0; Neon 0/0/0
email rollout approval/execution: yes/local-migration-applied-provider-pending
public backend/static: v351 Live
production approval/execution: no/no
```

## v377 구현과 private environment 준비

- `auth_rate_limit_buckets`는 scope와 domain-separated HMAC subject digest만 보존하고 원문 IP·email·username·identifier·Bearer/action token을 저장하지 않습니다. PostgreSQL upsert 후 row lock으로 동시 요청을 직렬화하고 fixed window, 반복 실패 cooldown, 유한 비동기 지연을 적용합니다.
- auth 9개 POST의 IP 검사는 pure ASGI middleware에서 FastAPI JSON 파싱·schema·Bearer dependency보다 먼저 실행됩니다. 유효한 body는 route에서 subject bucket을 합쳐 credential/token 실패를 두 bucket에 기록합니다.
- Render proxy mode는 Cloudflare가 덮어쓰는 단일 `CF-Connecting-IP`만 허용합니다. caller가 선행 값을 조작할 수 있는 `X-Forwarded-For`는 무시하고, 신뢰 header가 없거나 IP가 아니면 production에서 503 fail-closed합니다.
- `RequestBodyLimitMiddleware`는 auth 16,384 bytes, 전체 2,100,000 bytes를 JSON 파싱 전에 적용합니다. 선언 초과, 중복·충돌·잘못된 `Content-Length`, 실제 body 초과를 원문 반사 없이 413으로 차단합니다.
- `auth_email_outbox`는 user FK, purpose, HMAC target digest, 상태·시각·단일 시도 메타데이터만 저장합니다. 수신자·원문 token·메일 본문은 DB에 없습니다.
- worker는 `FOR UPDATE SKIP LOCKED`로 claim하고 preparing commit 뒤 recipient을 해석합니다. action token은 provider 호출 직전에 생성해 digest만 sending 상태와 commit합니다. provider 시도 후 실패·timeout·process crash는 자동 재시도하지 않고 unknown outcome을 terminal로 마감합니다.
- resend는 기존 유효 token을 먼저 폐기하지 않습니다. 새 provider 발송이 성공해야 다른 동일-purpose token을 소비하며, prepare·failed·unknown 상태에서는 이전 링크를 보존합니다.
- 인증 재전송·아이디 찾기·비밀번호 재설정 요청은 실제·decoy 모두 outbox transaction을 거친 뒤 350 ms + 0∼100 ms jitter와 generic 202로 답합니다. provider HTTPS 호출은 request transaction에서 실행하지 않습니다.
- 7일이 지난 미인증 identity는 active email/password legacy account이면서 admin·audit·save·item·inventory·equipment·skill·mailbox 관계가 없을 때만 동일 username/email 재가입 시 회수합니다.
- Bearer/session 실패는 stable code를 사용합니다. frontend는 이 allowlist에서만 session을 지우고, `invalid_credentials`·관리자 업무 403·429·413·code 없는 401/403에서는 token을 보존합니다.
- action-link fragment는 backend와 같은 `A-Za-z0-9_-` 32∼256자를 검사한 뒤 URL에서 즉시 제거합니다. backend가 `email_action_token_invalid`를 반환할 때만 메모리의 링크를 폐기합니다.
- 이메일 접수 UI는 “보냈습니다”가 아니라 “요청을 접수했습니다·도착까지 몇 분 걸릴 수 있음”을 보여줍니다.
- `email-validator==2.3.0`과 `dnspython==2.8.0`은 backend `.venv`와 재현 가능한 Linux lock에 고정되어 있으며 누락 시 이메일 동작은 fail-closed합니다.
- `prepare_v377_email_release.py`는 미래 release의 fresh publish lifecycle, 단일 `run_attempt=1`, 새 서명 image digest, 기존 Render service와 필수 환경변수 키 이름만 fail-closed로 검증합니다. 기본 동작은 read-only이며 GitHub·GHCR·Render·Brevo·공개 endpoint를 호출하지 않는 source-only guard입니다.
- `private_artifacts.py`와 환경·migration guard는 secret·DB backup·evidence를 읽기 전에 exact path와 OS별 비공개 권한을 검증합니다. Windows에서는 현재 사용자·LocalSystem·Administrators만 명시적으로 허용하며 secret/backup 내용은 private file을 먼저 만든 뒤 기록합니다. 기본 plan/inspect는 권한을 바꾸지 않습니다.
- 실제 environment `--apply`는 기존 security artifact 535개의 ACL을 비공개로 고정하고 local/production에 서로 다른 강한 email/abuse secret 4개를 값 출력 없이 생성해 완료했습니다. Brevo API key와 발신 이메일은 아직 없습니다.
- 이메일 없는 기존 v295 계정은 아이디·비밀번호 접근을 유지하면서 `emailVerified=false`로 반환합니다. 이메일이 있는 신규 계정은 인증 링크 완료 전 access token과 Bearer 접근을 계속 차단합니다.

## DB·migration 상태

- Alembic graph의 단일 head는 `v295_initial_schema → v371_email_identity_lifecycle → v377_auth_email_public_security`입니다.
- v377은 `auth_rate_limit_buckets`, `auth_email_outbox` 두 table과 관련 index·FK·CHECK만 추가합니다. v371 source를 수정하지 않습니다.
- actual local DB는 exact v377이고 Neon은 v295입니다. local apply는 1회, local/Neon stamp·downgrade와 Neon apply는 0회입니다.
- pushed SHA `8db9bcb`에서 isolated runner가 비민감 synthetic fixture의 `v295 → v377 → v295 → v377`을 1회 성공했습니다. 같은 SHA에서 local v295 custom backup 751 rows도 1회 성공했습니다.
- fingerprint canonicalization source 수정 뒤에는 위 roundtrip report와 local backup이 현재 SHA의 guard에 사용할 수 없는 stale evidence입니다. 파일과 marker는 역사 증거로 보존하고 삭제·덮어쓰기하지 않습니다.
- 첫 local apply는 Alembic 실행 전에 cross-driver fingerprint 표현 차이를 실제 차이로 잘못 판정해 안전 중단됐습니다. apply report는 없고 local DB는 v295 그대로이며 local apply attempt marker가 남아 같은 action을 재실행하지 않습니다.
- `345872a`의 별도 `recovery1` namespace에서 synthetic 왕복과 fresh local backup 751 rows를 성공한 뒤 local v295→v377을 정확히 1회 적용했습니다. 기존 22개 table 데이터 변화 0과 25개 model table parity를 확인했고 완료 report와 marker를 보존합니다.
- Neon은 접속하지 않았고 backup·apply·attempt marker도 없습니다.
- target backup/apply guard는 같은 clean pushed source SHA의 완료된 고정 roundtrip report와 fresh custom backup을 필수로 검증합니다. 기존 22 table은 migration 전 열과 PK 순서로 before/after digest가 정확히 일치해야 합니다.
- actual target apply는 한 synchronous PostgreSQL transaction에서 고정 5초 lock timeout·120초 statement timeout을 설정하고 기존 22개 table을 첫 SELECT 전에 정렬된 `SHARE ROW EXCLUSIVE`로 잠급니다. 같은 connection에서 fingerprint→backup 대조→Alembic→schema/data parity를 끝낸 뒤 한 번 commit하고, 실패하면 전체 rollback합니다. 일반 reader는 허용되고 writer만 유한 시간 대기하므로 Render pause는 필요 없습니다.
- PostgreSQL subprocess와 sync psycopg connection은 inherited `PG*` 값을 모두 제거합니다. Windows는 고정 PostgreSQL 16 절대 경로, POSIX는 root/current owner이면서 group/world non-writable인 resolved client 경로만 허용합니다.
- isolated roundtrip, local/Neon backup, local/Neon apply는 각각 첫 mutation 전에 private exclusive attempt marker를 만들며 성공·실패 후 수동·자동 재실행을 모두 거부합니다. actual target에 downgrade·stamp·restore·reset·seed 경로도 없습니다.
- production rollback은 DB를 additive v377에 둔 채 이전 application image로만 수행하며 actual DB downgrade를 사용하지 않습니다.

## 검증 결과

- v377 public auth security focused smoke: body cap, malformed/schema-invalid pre-parse IP limiter, HMAC key, concurrent-safe bucket, cooldown/delay, trusted Render IP, 429/413/no-store/CORS PASS
- v377 semantic outbox focused smoke: no recipient/raw token/body persistence, ordered claim·prepare·sending·finalize, provider 단일 시도, crash recovery, decoy, 기존 token 보존 PASS
- v377 migration parity/guard smoke: revision/model parity, fixed synthetic roundtrip과 target backup/apply one-attempt marker, private evidence chain, hostile libpq env 제거, trusted client path, single-transaction quiescent exact apply, legacy data preservation, Neon TLS boundary PASS
- v377 email environment temp-fixture smoke: ignored-only private atomic replacement, existing backup tree recursive ACL hardening, read-only plan non-mutation, strong secret preserve/distinct generation, no value output, external Brevo action report PASS
- v377 email release source guard smoke: 과거 v351 evidence·digest·deploy ID 재사용 차단, fresh publish lifecycle, 단일 dispatch·즉시 gate closure·rerun 금지, key-only Render 준비 PASS
- v371 email backend·frontend, v370 auth/character/admin, admin media contract·Neon production Settings focused 회귀 PASS
- 관련 Python Ruff·compileall, JavaScript syntax, runtime blocking-I/O, `git diff --check` PASS
- 설치된 Git Bash에서 backend `.venv`를 활성화하고 `DEBUG=false`로 실행한 전체 core smoke PASS
- aware datetime UTC 변환과 Decimal 고정값 canonicalization 회귀 및 실제 local 751행 asyncpg/psycopg read-only fingerprint parity PASS
- local v377 migration 후 인증 POST가 503 대신 정상 422/credential 판정까지 진행하고, 실제 브라우저에서도 보호 기능 오류가 사라짐을 확인했습니다.
- 이메일 있는 미인증 계정 차단과 이메일 없는 legacy 계정 로그인·Bearer 복구 회귀 PASS

## 실행하지 않은 것

- untouched Neon의 backup/apply, DB reset·seed·restore·stamp·actual downgrade
- Brevo 가입·sender 확인·전용 API key와 실제 provider/Render 설정, 실제 메일·메일 클라이언트 QA
- owner bootstrap apply
- GitHub Actions, GHCR image 게시, Render env·backend deploy, legacy static 배포
- custom domain, DNS, 결제

## 공개 전 필수 보강

v377에서 rate limit, durable outbox/queue, raw body cap, 미인증 계정 회수는 source 구현을 완료했습니다. 공개 회원가입과 새 backend/static 배포 전에는 다음이 남아 있습니다.

1. 서버측 session/refresh/revoke, 기기별 원격 폐기 또는 현재 access-token 정책 확정
2. 다중 기기 save revision/CAS와 충돌 해결
3. HTTPS/CSP/XSS 회귀, 브라우저 token 저장 정책
4. 개인정보 보관·삭제·문의·복구 정책
5. Brevo sender, anonymous tracking, 1개월 log retention, preview 미저장과 전용 API key 회전 실제 검증
6. backend image와 legacy static의 같은 exact-SHA 게시·배포·rollback 검증

source-only release guard는 이 마지막 실행을 대신하거나 허가하지 않습니다. 위 1∼5번과
Brevo 실제 검증이 끝난 뒤에만 별도 exact-SHA release 판단에 사용합니다.

## 바로 다음 단계

1. 기호가 Brevo Free 계정·sender 소유 확인·transactional privacy 설정·전용 API key를 준비합니다.
2. `BREVO_API_KEY`와 `BREVO_FROM_EMAIL`을 값 출력 없이 local dotenv에 넣고 backend를 재시작합니다.
3. 실제 테스트 메일 1건과 가입→인증→로그인→복구를 확인한 뒤 untouched Neon 단계를 별도 exact 범위로 진행합니다.

기호의 v376 승인과 이번 local 복구 요청은 이메일 인증 rollout에 계속 적용됩니다. Brevo 가입·발신자 소유 확인·privacy 설정·API key 생성처럼 Codex가 대신할 수 없는 행동만 모아 요청합니다. owner bootstrap, DB reset·seed·restore와 이메일 인증에 무관한 기능 변경은 포함되지 않습니다.

## 배포와 기존 게임 상태

- 공개 frontend: `https://gihohoho-upgrade-rpg.onrender.com/index.html`, `/admin.html`
- 공개 backend: `https://upgrade-rpg-api.onrender.com`
- 공개 backend/static은 계속 v351이고 v370/v371/v377 로컬 계정 기능은 배포하지 않았습니다.
- Neon PostgreSQL 16 Singapore는 아직 v295의 22 application tables + `alembic_version`입니다.
- GHCR은 `ghcr.io/gihohoho/upgrade-rpg-backend`, target은 `linux/amd64`입니다.
- 상세 인증 계약은 [이메일 인증·복구·삭제](ACCOUNT_EMAIL_VERIFICATION_RECOVERY_AND_DELETION.md), 기존 저장 계약은 [계정·캐릭터 슬롯](ACCOUNT_AUTH_AND_CHARACTER_SLOTS.md), 후속 gate는 [Security Gates](SECURITY_ROTATION_AND_GITHUB_GATES.md)를 따릅니다.
