# Upgrade RPG Codex handoff — v377

새 채팅은 루트 [AGENTS.md](AGENTS.md)를 먼저 읽고 이 문서를 이어서 사용합니다. 더 자세한 현재 상태는 [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)가 기준입니다.

```txt
latest: v377.local-email-e2e-verified
strict result: local-email-e2e-verified-provider-finalize-followup
next safe stage: diagnose-v377-brevo-delivery-finalize
source head: v377_auth_email_public_security
local/Neon DB current: v377_auth_email_public_security / v295_initial_schema
v377 apply/stamp/downgrade: local 1/0/0; Neon 0/0/0
email rollout approval/execution: yes/local-provider-e2e-verified-finalize-followup
public backend/static: v351 Live
```

## 이번 체크포인트

- v371 이메일 인증·복구·삭제 위에 v377 공개 요청 보호 source를 추가했고 local DB까지 v377로 적용했습니다. Neon과 공개 backend는 아직 각각 v295와 v351입니다.
- 9개 auth POST는 JSON 파싱·FastAPI dependency 전에 IP bucket을 먼저 소비하고, 유효한 body는 정규화 email·identifier·token·user bucket을 추가로 적용합니다. Render에서는 Cloudflare가 덮어쓰는 `CF-Connecting-IP`만 신뢰하고 `X-Forwarded-For`는 사용하지 않습니다.
- ASGI raw body cap은 auth 16 KiB, 전체 2,100,000 bytes이며 JSON 파싱 전에 선언·실제 크기를 모두 검증합니다. auth 응답은 `Cache-Control: no-store`를 유지합니다.
- `auth_email_outbox`는 수신자, 원문 action token, 렌더링 본문을 저장하지 않습니다. worker가 claim한 뒤 발송 직전에 token digest만 commit하며, provider 호출을 시작한 건은 자동 재시도하지 않습니다. 새 메일 발송이 성공해야만 이전 유효 링크를 폐기합니다.
- 계정 탐색 가능한 메일 요청은 provider를 기다리지 않고 고정·jitter 지연 후 generic `202` queue 접수로 답합니다. frontend는 202·429 `Retry-After`·413과 stable auth error code를 구분하며 유효 링크와 session을 오류 종류에 맞게 보존합니다.
- 7일이 지난 미인증 계정은 관리자·감사·게임 소유 데이터가 하나도 없을 때만 동일 identity 재가입 요청에서 안전하게 회수합니다.
- `v377_auth_email_public_security` revision은 v371의 단일 후속 head이며 rate bucket과 semantic outbox 두 table만 추가합니다.
- private environment 준비는 완료했습니다. ignored local/production dotenv와 기존 DB security artifact 535개의 ACL을 비공개로 고정하고 서로 다른 강한 email/abuse secret 4개를 값 출력 없이 생성했습니다. local `backend/.env`에는 값 출력 없이 프로젝트 전용 Brevo key와 검증된 sender를 추가했으며 Render production env는 바꾸지 않았습니다.
- `8db9bcb`의 stale evidence와 실패 marker는 삭제·덮어쓰기하지 않고 보존했습니다. `345872a`의 별도 `recovery1` DB·report·backup·marker에서 synthetic fixture의 `v295 → v377 → v295 → v377`과 local 751 legacy rows backup을 새로 검증했습니다.
- local DB는 같은 `345872a`에서 v377로 정확히 1회 upgrade했고 기존 22개 table 데이터 변화 0·25개 model table parity를 확인했습니다. stamp·downgrade·restore·reset·seed는 실행하지 않았습니다.
- 인증 POST의 `auth_protection_unavailable` 503이 사라졌고 브라우저 로그인 요청이 정상 credential 판정까지 진행됩니다. 이메일 없는 기존 v295 계정은 아이디·비밀번호 접근을 유지하면서 `emailVerified=false`로 표시하고, 이메일이 있는 신규 계정은 링크 인증 전 계속 차단합니다.
- Brevo transactional privacy는 anonymous tracking, 1개월 log retention, preview 미저장으로 확인했습니다. local 호출 IP를 허용한 뒤 실제 Naver 메일 1건 수신, 링크 인증 HTTP 200, 실제 계정 로그인과 빈 캐릭터 슬롯 8개 진입을 확인했습니다.
- 첫 발송은 IP 미허용 상태에서 401로 실패했고 자동 재시도하지 않았습니다. 허용 뒤 새 요청은 실제 메일을 전달했지만 outbox 행은 provider 응답 완료가 모호해 `delivery_outcome_unknown`으로 안전 종료됐습니다. 인증 token과 로그인은 정상 동작했으며 Neon 전에는 이 finalize 관찰을 집중 진단합니다.
- Neon은 접속하지 않았고 backup·apply marker도 없습니다.
- actual target apply는 한 PostgreSQL transaction 안에서 기존 22개 table을 첫 조회 전에 `SHARE ROW EXCLUSIVE`로 잠근 뒤 fingerprint→backup 대조→Alembic→schema/data parity를 끝내고 commit합니다. 일반 조회는 유지하고 concurrent write만 유한 시간 차단하므로 Render를 멈추지 않습니다.
- inherited `PGHOSTADDR`·`PGSERVICE`·`PGOPTIONS` 등 모든 `PG*` 기본값은 PostgreSQL subprocess와 sync connection에서 제거합니다. Windows client는 고정 PostgreSQL 16 절대 경로, POSIX client는 trusted owner와 group/world non-writable 경로만 허용합니다.
- 기존 `8db9bcb` marker와 `recovery1` evidence는 모두 역사 증거로 보존하며 같은 action을 다시 실행하지 않습니다.
- source-only email release guard는 미래 배포의 fresh GitHub publish lifecycle, 단일 시도·즉시 closure·rerun 금지, 새 서명 image digest, 기존 Render service와 필수 env key-name-only evidence만 검증합니다. 외부 network/provider를 호출하지 않았고 현재 공개 v351을 바꾸거나 배포 gate를 해제하지 않았습니다.
- `email-validator==2.3.0`·`dnspython==2.8.0`은 backend `.venv`과 Linux runtime/musllinux/dev lock에 고정되어 있습니다.
- v377 focused 검사와 설치된 Git Bash·backend `.venv`·`DEBUG=false` 조건의 전체 core smoke는 PASS했습니다. local migration은 완료됐지만 Neon migration·provider 발송·공개 배포 완료를 뜻하지 않습니다.
- owner bootstrap은 이 rollout과 분리된 one-shot이며 실행하지 않습니다.

## 바로 할 일

1. 실제 메일 전달 뒤 outbox가 `sent` 대신 `delivery_outcome_unknown`으로 닫힌 원인을 provider response·worker finalize 경계에서 집중 진단합니다.
2. token·수신자·API key를 출력하지 않는 focused 회귀로 정상 2xx 응답의 `sent` finalize와 timeout의 terminal unknown을 구분해 검증합니다.
3. 진단·필요한 source 수정이 끝난 뒤에만 untouched Neon의 fresh backup·exact v377 apply를 별도 exact 범위로 진행합니다.

배포를 판단할 때만 `deploy/v377-email-release-guard.example.json`과
`tools/prepare_v377_email_release.py`의 source-only 계약을 사용하며, 준비됐다는 사실을 실제
GitHub Actions/GHCR/Render 실행이나 승인으로 해석하지 않습니다.

## 안전 경계와 아직 실행하지 않은 것

- 실제 secret·token·password·DB URL은 출력·문서·Git artifact에 남기지 않습니다.
- `345872a` recovery1 synthetic 왕복·local backup·local v377 apply는 각각 1회 완료됐습니다. local stamp·downgrade는 0회이고 Neon apply·stamp·downgrade도 0회입니다.
- local DB는 v377이며 Neon은 untouched v295입니다. 기존 실패 marker와 새 완료 evidence는 모두 보존합니다.
- local Brevo 설정과 실제 메일 E2E는 완료했습니다. GitHub Actions/GHCR, Render env·deploy, static 배포는 실행하지 않았습니다.
- DB reset·seed·restore·stamp, 실제 DB downgrade, production 자동 retry는 허용되지 않습니다. 운영 rollback은 DB를 additive v377에 두고 이전 app image로만 돌립니다.
- 기호는 실질적인 이메일 인증 기능 rollout을 승인했고 이 범위는 다시 승인받지 않습니다. Brevo 가입·발신자 소유 확인·API key 입력도 완료됐습니다.
- 공개 회원가입·새 backend/static 배포는 server session/revoke, save revision/CAS, CSP/XSS·브라우저 token, 개인정보 정책이 남아 차단 상태입니다.
- 공개 frontend/backend는 계속 v351입니다.

## 문서 기준

- 현재 판단: `docs/current/`
- 장기 기술 자료: `docs/reference/`
- 자동 생성 보고서: `docs/generated/`
- API 계약: `docs/contracts/`
- 실행 안내: `docs/guides/`
- 완료 이력: `docs/archive/history/`

문서 체계는 [Documentation System](docs/DOCUMENTATION_SYSTEM.md), 전체 색인은 [Docs Hub](docs/README.md)가 기준입니다.
