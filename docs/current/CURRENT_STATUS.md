# Current Status — v377

이 문서는 현재 구현과 승인 경계를 설명합니다. 장기 작업 규칙은 루트 [AGENTS.md](../../AGENTS.md), 새 채팅의 바로 다음 행동은 [NEXT_CHAT_HANDOFF.md](../../NEXT_CHAT_HANDOFF.md)가 기준입니다.

## 상태 표식

```txt
latest: v377.public-email-rollout-deployed
strict result: public-email-rollout-deployed
next safe stage: monitor-v377-public-email-delivery-and-remaining-account-gates
local Alembic source head: v377_auth_email_public_security
local/Neon DB current: v377_auth_email_public_security / v377_auth_email_public_security
v377 apply/stamp/downgrade: local 1/0/0; Neon 1/0/0
email rollout approval/execution: yes/public-live
public backend/static: v377 Live
production approval/execution: yes/yes
```

## v377 구현과 환경

- `auth_rate_limit_buckets`는 원문 IP·email·username·identifier·Bearer/action token 대신 domain-separated HMAC digest만 보존합니다. PostgreSQL upsert와 row lock으로 동시 요청을 직렬화하고 fixed window, 반복 실패 cooldown, 유한 지연을 적용합니다.
- auth 9개 POST의 IP 검사는 JSON 파싱·schema·Bearer dependency 전에 실행됩니다. Render production은 edge가 덮어쓰는 `CF-Connecting-IP`만 신뢰하고 `X-Forwarded-For`를 사용하지 않습니다.
- raw body cap은 auth 16,384 bytes, 전체 2,100,000 bytes입니다. auth 응답은 202·422·429·413·5xx를 포함해 `Cache-Control: no-store`를 유지합니다.
- durable outbox/queue인 `auth_email_outbox`는 user FK, purpose, HMAC target digest, 상태·시각·단일 시도 메타데이터만 저장합니다. 수신자, 원문 action token, 메일 본문은 저장하지 않습니다.
- worker는 `FOR UPDATE SKIP LOCKED`로 claim하고 provider 호출 직전에 token digest만 commit합니다. provider를 시작한 건은 자동 재시도하지 않으며 새 발송이 성공해야만 이전 유효 링크를 폐기합니다.
- 인증 재전송·아이디 찾기·비밀번호 재설정은 실제·decoy 모두 고정+jitter 지연 뒤 generic 202로 답해 계정 존재 여부를 숨깁니다.
- 7일이 지난 미인증 계정은 관리자·감사·게임 소유 데이터가 없을 때만 동일 identity 재가입에서 회수합니다.
- frontend는 stable auth code를 분류해 유효 session과 action link를 보존합니다. 202 접수, 429 `Retry-After`, 413, backend와 동일한 action token 형식을 처리합니다.
- private environment 준비는 기존 security artifact 535개의 Windows ACL을 비공개로 고정하고 local/production에 서로 다른 email/abuse secret 4개를 값 출력 없이 생성했습니다.
- `email-validator==2.3.0`과 `dnspython==2.8.0`은 backend `.venv`와 Linux runtime/musllinux/dev lock에 고정되어 있습니다.
- local Brevo E2E에서 실제 Naver 메일 수신, action-link 인증 HTTP 200, 로그인, 캐릭터 슬롯 8개 진입을 확인했습니다. anonymous tracking, 1개월 log retention, preview 미저장도 확인했습니다.

## DB·migration 상태

- Alembic graph의 단일 head는 `v295_initial_schema → v371_email_identity_lifecycle → v377_auth_email_public_security`입니다.
- v377은 `auth_rate_limit_buckets`, `auth_email_outbox` 두 table과 관련 index·FK·CHECK를 추가합니다.
- `8db9bcb`의 첫 증거는 fingerprint canonicalization 뒤 stale이 되었고 실패·attempt marker와 함께 역사 증거로 보존합니다. 삭제·덮어쓰기·같은 action 재실행은 하지 않습니다.
- 첫 local apply는 Alembic 전에 cross-driver fingerprint 표현 차이를 실제 차이로 판정해 안전 중단됐습니다. 별도 `recovery1` namespace에서 synthetic 왕복, fresh local backup 751 rows, local v295→v377 apply를 각각 1회 완료했습니다.
- 최종 `recovery2` namespace에서 synthetic `v295 → v377 → v295 → v377`을 1회 완료했습니다. 같은 report로 Neon v295 fresh custom backup과 exact v377 apply를 각각 1회 완료했습니다.
- Neon apply report는 이전 revision v295, 현재 revision v377, legacy 22 tables·748 rows·데이터 변화 0, model 25 tables·차이 0을 기록합니다.
- 실제 apply는 5초 lock timeout·120초 statement timeout을 둔 단일 synchronous PostgreSQL transaction에서 기존 22 tables를 첫 SELECT 전에 `SHARE ROW EXCLUSIVE`로 잠그고 fingerprint→backup 대조→Alembic→schema/data parity 뒤 commit했습니다.
- local/Neon apply는 각각 1회이며 stamp·downgrade·restore·reset·seed는 모두 0회입니다. production rollback은 additive v377 DB를 유지하고 이전 application image로만 수행합니다.
- inherited `PG*` 값 제거, trusted PostgreSQL client path, private exclusive attempt marker와 report는 계속 fail-closed 경계로 유지합니다.

## 공개 배포 상태

- GitHub publish preparation `d58d093fc5ac2a4ffefa812e7067cb3083ce8a7d` 뒤 authorization `e5d8724017a446be0eabadcfdfdc982aa8c0af3f`, immediate closure `42fbf0a48b0431c5ce4b9e26bc0a1e47548b6534`, success record `ceea14c20ac8604d453930d8f6c5127f00236352`를 push했습니다.
- GitHub Actions run `32576889295`, `run_attempt=1`은 validate, local build/SBOM/Trivy, publish/attest/sign/verify를 모두 성공했습니다. rerun은 하지 않았습니다.
- 새 production image는 `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:a91d020c6b8abfbbcca56c1ff3ff7736c155fd43d854398e42bb0e42450ec994`입니다.
- Render backend service에는 email/security 환경변수 35개를 key-name-only로 확인하고 secret 값 노출 없이 저장했습니다. deploy `dep-da4qqi3tqb8s738l68h0`은 새 digest로 live입니다.
- legacy static deploy `dep-da4qr867bikc73aekck0`은 commit `ceea14c20ac8604d453930d8f6c5127f00236352`를 build해 live입니다.
- 공개 backend health는 HTTP 200입니다. 공개 인증 POST는 schema-invalid 요청에 422, 허용된 Naver 테스트 주소의 인증메일 재요청에 generic 202 accepted를 반환했고 두 응답 모두 `Cache-Control: no-store`였습니다.
- 이전 `auth_protection_unavailable`과 “이메일 보안 설정이 아직 준비되지 않았습니다” 503은 공개 경로에서 재현되지 않습니다.
- 공개 index는 로그인·회원가입·계정 찾기·인증 도움 UI를 표시하며 admin은 미로그인 상태에서 관리자 계정 확인 gate를 표시합니다.

## 검증 결과

- v377 auth security, semantic outbox, migration parity/guard, private environment, email release focused smoke PASS
- v371 email backend/frontend와 v370 auth/character/admin 회귀 PASS
- Python Ruff·compileall, JavaScript syntax, runtime blocking-I/O, Git Bash + backend `.venv` + `DEBUG=false` 전체 core smoke PASS
- recovery2 synthetic roundtrip, Neon backup, single-transaction apply, legacy data 보존, model parity PASS
- GHCR 서명 검증, Render backend internal health, public health, backend/static live 확인 PASS

## 실행하지 않은 것

- owner bootstrap apply
- DB reset·seed·restore·stamp·actual downgrade, production automatic retry
- custom domain, DNS, 결제
- 공개 테스트 메일함의 이번 재요청 메일 도착 확인과 provider log/outbox 관찰
- server session/refresh/revoke, save revision/CAS, CSP/XSS·브라우저 token 정책, 개인정보 정책 구현

## 공개 전 필수 보강

v377 rate limit, durable outbox/queue, raw body cap, 미인증 계정 회수와 이메일 rollout은 공개 배포됐습니다. 공개 회원가입을 확대하기 전에는 다음이 남아 있습니다.

1. 서버측 session/refresh/revoke와 기기별 원격 폐기 정책
2. 다중 기기 save revision/CAS와 충돌 해결
3. HTTPS/CSP/XSS 회귀와 브라우저 token 저장 정책
4. 개인정보 보관·삭제·문의·복구 정책
5. 공개 이메일 delivery 관찰과 secret 회전·운영 보관 절차

## 바로 다음 단계

1. 허용된 Naver 테스트 메일함에서 공개 재요청의 실제 도착 여부를 확인합니다.
2. secret·수신자·본문 없이 Render log와 outbox terminal 상태를 관찰합니다. 자동 재요청은 하지 않습니다.
3. 남은 공개 계정 gate를 하나씩 구현하고 각 범위에 맞는 focused 검증을 수행합니다.

## 배포 주소

- 공개 frontend: `https://gihohoho-upgrade-rpg.onrender.com/index.html`, `/admin.html`
- 공개 backend: `https://upgrade-rpg-api.onrender.com`
- GHCR repository: `ghcr.io/gihohoho/upgrade-rpg-backend`, target `linux/amd64`
- 상세 인증 계약은 [이메일 인증·복구·삭제](ACCOUNT_EMAIL_VERIFICATION_RECOVERY_AND_DELETION.md), 저장 계약은 [계정·캐릭터 슬롯](ACCOUNT_AUTH_AND_CHARACTER_SLOTS.md), 후속 gate는 [Security Gates](SECURITY_ROTATION_AND_GITHUB_GATES.md)를 따릅니다.
