# Upgrade RPG Codex handoff — v377

새 채팅은 루트 [AGENTS.md](AGENTS.md)를 먼저 읽고 이 문서를 이어서 사용합니다. 더 자세한 현재 상태는 [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)가 기준입니다.

```txt
latest: v377.local-migration-preflight-safe-stop
strict result: local-migration-preflight-safe-stop
next safe stage: prepare-v377-stale-evidence-recovery
source head: v377_auth_email_public_security
local/Neon DB current: v295_initial_schema
v377 apply/stamp/downgrade: 0/0/0
email rollout approval/execution: yes/private-env-prepared-db-preflight-safe-stop
public backend/static: v351 Live
```

## 이번 체크포인트

- v371 이메일 인증·복구·삭제 위에 v377 공개 요청 보호 source를 추가했습니다. 실제 local/Neon DB는 아직 v295이며 source만 v377입니다.
- 9개 auth POST는 JSON 파싱·FastAPI dependency 전에 IP bucket을 먼저 소비하고, 유효한 body는 정규화 email·identifier·token·user bucket을 추가로 적용합니다. Render에서는 Cloudflare가 덮어쓰는 `CF-Connecting-IP`만 신뢰하고 `X-Forwarded-For`는 사용하지 않습니다.
- ASGI raw body cap은 auth 16 KiB, 전체 2,100,000 bytes이며 JSON 파싱 전에 선언·실제 크기를 모두 검증합니다. auth 응답은 `Cache-Control: no-store`를 유지합니다.
- `auth_email_outbox`는 수신자, 원문 action token, 렌더링 본문을 저장하지 않습니다. worker가 claim한 뒤 발송 직전에 token digest만 commit하며, provider 호출을 시작한 건은 자동 재시도하지 않습니다. 새 메일 발송이 성공해야만 이전 유효 링크를 폐기합니다.
- 계정 탐색 가능한 메일 요청은 provider를 기다리지 않고 고정·jitter 지연 후 generic `202` queue 접수로 답합니다. frontend는 202·429 `Retry-After`·413과 stable auth error code를 구분하며 유효 링크와 session을 오류 종류에 맞게 보존합니다.
- 7일이 지난 미인증 계정은 관리자·감사·게임 소유 데이터가 하나도 없을 때만 동일 identity 재가입 요청에서 안전하게 회수합니다.
- `v377_auth_email_public_security` revision은 v371의 단일 후속 head이며 rate bucket과 semantic outbox 두 table만 추가합니다.
- private environment 준비는 완료했습니다. ignored local/production dotenv와 기존 DB security artifact 535개의 ACL을 비공개로 고정하고 서로 다른 강한 email/abuse secret 4개를 값 출력 없이 생성했습니다. Brevo key와 발신 이메일은 아직 없습니다.
- pushed SHA `8db9bcb`에서 synthetic fixture의 `v295 → v377 → v295 → v377` 왕복은 성공했습니다. 이후 fingerprint canonicalization source를 수정했으므로 이 보고서는 현재 SHA의 apply gate에 사용할 수 없는 stale evidence입니다.
- 같은 `8db9bcb`에서 local v295 custom backup 751 rows를 성공적으로 만들었지만 이것도 새 SHA에는 stale입니다. 첫 local apply는 Alembic 전에 cross-driver fingerprint 표현 차이로 안전 중단됐고 apply report는 없으며 local DB는 v295 그대로입니다.
- isolated roundtrip·local backup·local apply marker는 성공·실패와 관계없이 보존합니다. 기존 action 재실행, marker/evidence 삭제·덮어쓰기, 자동 retry는 하지 않습니다. Neon은 접속하지 않았고 backup·apply marker도 없습니다.
- actual target apply는 한 PostgreSQL transaction 안에서 기존 22개 table을 첫 조회 전에 `SHARE ROW EXCLUSIVE`로 잠근 뒤 fingerprint→backup 대조→Alembic→schema/data parity를 끝내고 commit합니다. 일반 조회는 유지하고 concurrent write만 유한 시간 차단하므로 Render를 멈추지 않습니다.
- inherited `PGHOSTADDR`·`PGSERVICE`·`PGOPTIONS` 등 모든 `PG*` 기본값은 PostgreSQL subprocess와 sync connection에서 제거합니다. Windows client는 고정 PostgreSQL 16 절대 경로, POSIX client는 trusted owner와 group/world non-writable 경로만 허용합니다.
- 향후 recovery도 기존 marker를 우회하지 않고 새 namespace·artifact·confirmation을 가진 별도 절차와 exact 승인을 먼저 요구합니다.
- source-only email release guard는 미래 배포의 fresh GitHub publish lifecycle, 단일 시도·즉시 closure·rerun 금지, 새 서명 image digest, 기존 Render service와 필수 env key-name-only evidence만 검증합니다. 외부 network/provider를 호출하지 않았고 현재 공개 v351을 바꾸거나 배포 gate를 해제하지 않았습니다.
- `email-validator==2.3.0`·`dnspython==2.8.0`은 backend `.venv`과 Linux runtime/musllinux/dev lock에 고정되어 있습니다.
- v377 focused 검사와 설치된 Git Bash·backend `.venv`·`DEBUG=false` 조건의 전체 core smoke는 모두 PASS했습니다. 이 결과는 actual local/Neon migration 완료를 뜻하지 않습니다.
- owner bootstrap은 이 rollout과 분리된 one-shot이며 실행하지 않습니다.

## 바로 할 일

1. `8db9bcb` evidence가 SHA-stale이고 기존 attempt가 소비됐다는 사실을 전제로 새 recovery namespace·artifact·confirmation 계약을 준비합니다.
2. 기존 marker나 evidence를 지우거나 같은 action을 재실행하지 않습니다. 새 recovery 절차와 exact 실행 범위를 별도로 검토·승인받기 전에는 local/Neon DB 단계로 진행하지 않습니다.
3. 승인된 recovery가 새 SHA의 fresh evidence를 만들 때만 local을 다시 검토하고, 그 성공 뒤에 untouched Neon의 backup·exact v377 apply를 별도 순서로 진행합니다.
4. DB 단계가 끝난 뒤 Brevo 가입·sender 소유 확인·전용 API key 입력처럼 Codex가 대신할 수 없는 행동만 기호에게 한 번에 요청하고 실제 테스트 메일과 가입→인증→로그인→복구를 확인합니다.

배포를 판단할 때만 `deploy/v377-email-release-guard.example.json`과
`tools/prepare_v377_email_release.py`의 source-only 계약을 사용하며, 준비됐다는 사실을 실제
GitHub Actions/GHCR/Render 실행이나 승인으로 해석하지 않습니다.

## 안전 경계와 아직 실행하지 않은 것

- 실제 secret·token·password·DB URL은 출력·문서·Git artifact에 남기지 않습니다.
- synthetic isolated 왕복과 local read-only custom backup은 `8db9bcb`에서 각각 1회 완료됐지만 새 SHA에는 stale입니다. actual local/Neon apply·stamp·downgrade는 0회입니다.
- local apply attempt는 Alembic 전에 안전 중단됐고 report 없이 marker만 남았습니다. local DB는 v295이며 Neon은 untouched입니다.
- Brevo 설정·실제 메일, GitHub Actions/GHCR, Render env·deploy, static 배포는 실행하지 않았습니다.
- DB reset·seed·restore·stamp, 실제 DB downgrade, production 자동 retry는 허용되지 않습니다. 운영 rollback은 DB를 additive v377에 두고 이전 app image로만 돌립니다.
- 기호는 실질적인 이메일 인증 기능 rollout을 승인했고 이 범위는 다시 승인받지 않습니다. Brevo 가입·발신자 소유 확인·API key 입력만 사용자 행동으로 남습니다.
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
