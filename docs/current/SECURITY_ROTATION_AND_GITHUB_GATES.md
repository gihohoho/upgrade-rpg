# Security rotation and GitHub gates — v377

## v377 public email rollout deployed — 2026-08-22

- Alembic source head는 `v295_initial_schema` → `v371_email_identity_lifecycle` →
  `v377_auth_email_public_security`입니다. v377은 `auth_rate_limit_buckets`와
  `auth_email_outbox`를 추가했고 local/Neon DB에 v377을 각각 정확히 1회 적용했습니다.
  Neon stamp·downgrade·restore·reset·seed는 실행하지 않았습니다.
- 인증 rate bucket은 IP·이메일·아이디·user·action token 원문 대신 별도
  `AUTH_ABUSE_SECRET` HMAC-SHA256 digest와 source-controlled scope만 PostgreSQL에
  저장합니다. 반복 실패 cooldown·응답 지연과 오래된 bucket retention도 DB 상태를
  기준으로 합니다.
- Render production은 Cloudflare edge가 덮어쓴 정확한 `CF-Connecting-IP` 한 값만 client
  IP로 신뢰합니다. caller-controlled 첫 값이 남을 수 있는 `X-Forwarded-For`는 사용하지
  않습니다. header 누락·잘못된 값·DB rate store 오류는 요청 제한을 건너뛰지 않고
  `503 auth_protection_unavailable`로 fail-closed합니다.
- pure-ASGI middleware는 FastAPI JSON parsing 전에 `/api/v1/auth` request body를
  16,384바이트, 그 밖의 전체 HTTP body를 2,100,000바이트로 제한합니다. 선언 길이가
  없거나 실제보다 작아도 수신 byte를 세고, 초과·framing 불일치는 `413
  request_body_too_large`로 닫습니다.
- 인증 응답은 source-controlled stable code와 `Cache-Control: no-store`를 사용합니다.
  rate limit은 `429 auth_rate_limited`, `Retry-After` header와 같은 초 수의 response meta를
  반환합니다. discovery 경로는 queue 접수를 뜻하는 같은 `202` 문구와 최소 응답
  시간+jitter로 계정 존재·실제 전송 여부 차이를 줄입니다.
- outbox는 purpose, HMAC target digest, 상태, 최대 1회 provider attempt와 제한된 provider
  message ID/error code만 보관합니다. 수신자 주소, 원문 token, 제목·본문은 DB에 저장하지
  않습니다. worker가 `FOR UPDATE SKIP LOCKED`로 claim한 뒤에만 현재 수신자·token·본문을
  메모리에서 만들고 Brevo HTTPS API를 호출합니다.
- 공급자 호출을 시도한 job은 timeout·오류·결과 불명과 관계없이 자동 retry하지 않습니다.
  호출 전 멈춘 `preparing`만 다시 pending으로 돌리고 오래된 `sending`은 결과 불명 실패로
  끝냅니다. 재전송한 새 메일이 성공한 뒤에만 같은 목적의 이전 유효 token을 소진하므로
  공급자 실패가 기존 정상 link를 깨뜨리지 않습니다.
- 생성 후 168시간이 지난 미인증 identity는 background bulk delete하지 않습니다. 같은
  identity의 새 가입 요청에서 non-admin·active·password-backed이고 role·save·item·slot·
  skill·mail·관리자 감사 데이터가 전혀 없을 때만 row lock 아래 회수합니다.
- action link는 고정 `PUBLIC_FRONTEND_ORIGIN` fragment만 사용하고 Host·return URL을
  신뢰하지 않습니다. 프런트는 fragment를 즉시 history에서 제거하고,
  `email_action_token_invalid`일 때만 현재 link를 폐기합니다. `429`·`413`·network/`5xx`에는
  탭 메모리의 link를 보존합니다.
- 이메일 token 원문은 DB에 저장하지 않고 별도 `EMAIL_TOKEN_SECRET` HMAC digest만 둡니다.
  `AUTH_ABUSE_SECRET`, `EMAIL_TOKEN_SECRET`, JWT와 admin dev key는 production에서 서로
  다른 32자 이상 secret이어야 하며 실제 값은 Git·채팅·출력에 넣지 않습니다.
- `email-validator 2.3.0`과 `dnspython 2.8.0`은 backend `.venv`와 Linux lock에 반영됐고,
  dependency·secret·worker·Brevo 설정이 빠지면 약한 fallback이나 직접 발송 없이
  fail-closed합니다.
- ignored local/production dotenv와 DB backup·migration evidence는 내용을 읽기 전에 exact
  path와 private permission을 검증합니다. Windows는 ACL 상속을 끄고 현재 사용자,
  LocalSystem, Builtin Administrators 세 SID만 FullControl로 허용하며, POSIX는 현재 owner의
  `0600`/`0700`만 허용합니다. environment `--apply`는 기존 security artifact 535개의 ACL을
  재귀적으로 고치고 local/production에 서로 다른 강한 email/abuse secret 4개를 값 출력 없이
  기록해 완료했습니다.
- migration guard는 inherited `PGHOSTADDR`·`PGSERVICE`·`PGOPTIONS`를 포함한 모든 `PG*`
  기본값을 subprocess와 sync psycopg connect 시점에 제거합니다. Windows PostgreSQL 16
  client는 고정 절대 경로, POSIX client는 root/current owner와 group/world non-writable
  resolved 경로만 허용합니다. isolated roundtrip과 target별 backup·apply는 첫 mutation 전에
  private exclusive marker를 남겨 성공·실패 후 같은 시도를 다시 실행하지 못하게 합니다.
- Brevo account와 검증된 sender, 1개월 만료 project API key, anonymous tracking, 1개월
  log retention, preview 미저장을 local 범위에서 준비했습니다. key와 sender 값은 ignored
  `backend/.env`에 보존하고 Render에는 필요한 값만 UI를 통해 전달했습니다. 일반 Brevo API key는
  account-wide 권한이므로 노출·미사용·integration 종료 시 삭제합니다.
- local 호출 IP 허용 뒤 실제 Naver 메일 수신, 링크 인증과 로그인을 확인했습니다. 실제 전달된
  요청의 `delivery_outcome_unknown`은 여러 local reload worker의 ownership 단절로 좁혔고,
  단일 직접 provider 진단은 2초 이내 message ID를 정상 반환했습니다. 자동 재시도는 하지 않았습니다.
- v377 public-security·semantic-outbox와 기존 v371 이메일 lifecycle focused source 검사,
  backend `.venv`·`DEBUG=false` 조건의 v377 전체 core smoke는 PASS입니다. pushed SHA
  `8db9bcb`에서 synthetic migration 왕복도 성공했지만 fingerprint canonicalization source
  수정 뒤에는 현재 SHA의 apply gate에 사용할 수 없는 stale evidence입니다.
- `deploy/v377-email-release-guard.example.json`과 `tools/prepare_v377_email_release.py`는
  미래 release마다 fresh GitHub publish lifecycle, 단일 `run_attempt=1`, 즉시 authorization
  closure, rerun 금지, 새 서명 image digest, 기존 Render service와 필수 env key-name-only
  evidence를 요구합니다. `smoke_v377_email_release.py`가 과거 v351 evidence·digest·deploy ID
  재사용과 secret value·provider endpoint 기록을 차단하는 source 계약을 검증했습니다.
  기본 guard는 외부 network/provider mutation을 하지 않으며 배포 승인이나 실행이 아닙니다.
- local DB는 recovery1 evidence로, Neon은 recovery2 synthetic 왕복과 fresh backup evidence로
  v377에 각각 정확히 1회 적용했습니다. GitHub Actions run `32576889295`의 단일 attempt가
  signed digest `sha256:a91d020c6b8abfbbcca56c1ff3ff7736c155fd43d854398e42bb0e42450ec994`를 게시했고,
  Render backend `dep-da4qqi3tqb8s738l68h0`과 static `dep-da4qr867bikc73aekck0`이 live입니다.
  owner bootstrap은 실행하지 않았습니다.
- production 메일 장애 조사에서 Brevo가 Render shared outbound IP를 차단한 사실을 확인했습니다.
  Render 공식 CIDR `74.220.52.0/24`, `74.220.60.0/24`만 Brevo Authorized IP에 등록했고,
  이후 인증 메일은 provider에서 Delivered로 확인됐습니다.
- 실제 전송 뒤 outbox가 `sending`에 남은 것은 성공 finalize가 `completed_at`보다 먼저 `sent`를
  autoflush해 DB CHECK 제약을 위반했기 때문입니다. `de3ae5d`에서 원자적 상태 설정 순서를 고치고
  회귀 검사를 추가했습니다.
- 사용자 승인 preparation `cd357de032425138d44323dd3060bbbf5b6a45d8`에서 authorization
  `46c9e7e33d866b160b6f4a8f36d5b68dabe3ece4`, immediate closure
  `e07474d5b5411dd805736687d1003f451298dae4`, evidence record
  `3e3516299a72e47c6d85597f8c0b60db5cb11a46`를 push했습니다. GitHub Actions run
  `32587614153`의 단일 attempt가 signed digest
  `sha256:80e8f57618b2bd8bbac37fd63381e454434e06b67eff0cd8f4327796bdc1c677`를 게시했고,
  Render backend `dep-da4tp7nqj5pc73b6l910`이 live입니다. 배포 뒤 공개 비밀번호 재설정 요청의
  outbox/token은 1회 시도 `sent`, provider 기록 존재, 오류 없음으로 마감됐습니다.

v376에서 기호는 이메일 인증 rollout에 한해 공개 보안 구현 → isolated migration 왕복 →
local/Neon의 새 backup·exact migration → Brevo sender/key/secret → 테스트 메일 → 필요한
backend/static release 준비를 한 범위로 승인했습니다. 정상 경로의 같은 DB 단계를 반복
승인받지는 않지만, 소비된 one-attempt marker 뒤 새 recovery는 단순 재시도가 아니므로 새
namespace와 exact 범위를 별도로 승인받습니다. Codex가 대신할 수 없는 Brevo 가입·발신자
소유 확인·privacy 설정·API key 입력은 완료했으며 owner bootstrap은 이 승인과 분리합니다.

첫 local apply의 safe-stop evidence는 보존했고, 별도 recovery1/recovery2 namespace에서 local과
Neon의 synthetic 왕복·fresh backup·exact v377 apply를 각각 1회 완료했습니다. 공개 health 200,
auth 422/202와 `Cache-Control: no-store`를 확인했습니다. 다음 안전 단계는 공개 delivery 관찰과
서버 session/refresh·기기별 폐기, save revision/CAS, CSP/XSS와 browser token,
개인정보·법적 보존 정책입니다. 자세한 계약은
`ACCOUNT_EMAIL_VERIFICATION_RECOVERY_AND_DELETION.md`에 있습니다. source-only release guard는
이 blocker를 해제하거나 우회하지 않습니다.

## v370 계정 인증 로컬 구현 보안 상태 — 2026-08-10

- v370은 회원가입·로그인, 계정별 캐릭터 슬롯 8개와 관리자 회원 관리를 로컬
  source에 구현한 단계입니다. 공개 Render backend와 Static Site는 계속 v351이며
  v370 인증 경로는 아직 공개되지 않았습니다.
- 새 secret을 만들지 않았습니다. access token 서명에는 이미 Render/local에 준비된
  기존 `JWT_SECRET_KEY`, 최초 관리자와 위험한 관리자 apply의 두 번째 방어선에는 기존
  `ADMIN_WRITE_DEV_KEY`를 사용합니다. 실제 값은 조회·출력·문서화하지 않았습니다.
- 비밀번호는 직접 dependency인 `bcrypt 5.0.0`으로만 해시합니다. 회원가입은
  `is_admin=false`로 고정하고 원문·해시, access token, 전체 save snapshot을 관리자
  응답과 로그에 포함하지 않습니다.
- access token은 알고리즘을 HS256으로 고정하고 종류·발급 시각·만료 시각·서명을
  확인합니다. 각 요청에서 DB 계정의 활성 상태를 다시 읽어 정지된 계정은 기존 token도
  다음 요청부터 거절합니다.
- 브라우저는 로그인 유지가 꺼져 있으면 `sessionStorage`, 사용자가 명시적으로 켜면
  `localStorage`에 token을 저장합니다. 이는 XSS 영향 범위가 있으므로 공개 전 CSP/XSS
  회귀와 저장 정책을 다시 검토합니다.
- 최초 관리자 지정은 로그인 가능한 관리자가 없을 때 현재 로그인 계정과 dev key를
  함께 확인하는 1회 bootstrap입니다. 회원 상태 apply는 관리자 Bearer 권한과 dev key,
  preview/stale 검사, 본인·마지막 관리자 보호, `AdminChangeLog` 기록을 모두 요구합니다.
- 저장 서비스는 인증 계정·고정 슬롯 키·캐릭터 고유 ID를 모두 대조하고 안정 직렬화된
  저장 요청을 2,000,000바이트로 제한합니다. JSON 파싱 전 ASGI raw request body cap은
  아직 없으므로 공개 전 별도 보강합니다.
- 정상 load는 서버 DB snapshot을 authoritative로 사용합니다. backend가 비어 있을 때만
  계정·캐릭터가 일치하는 local을 초기 복구 원본으로 사용합니다. 서버본과 다른 local은
  `.pre-backend-recovery`로 보존한 뒤 서버본을 사용합니다.
- 저장 실패의 `pending-unsynced` marker가 있으면 local 재전송·서버본 사용·취소를 게임
  UI 모달에서 명시적으로 선택하게 하고 결정 전 두 원본을 보존합니다. 자동·수동·전환
  저장은 단일 직렬 큐를 통과하며 전환은 runtime pause → queue drain → 상태 정리 순서입니다.
- 저장·세션 확인의 `401/403`은 local과 미전송 marker를 보존하고 token을 폐기해 재로그인
  복구 선택으로 이어집니다. network/timeout/`5xx`는 token·선택 상태를 유지하고 retry를
  허용합니다. 서버 revision과 낙관적 잠금이 아직 없어 다중 기기 동시 접속의 최신본 충돌
  정책은 공개 전 별도 보강합니다.
- 인증 FastAPI `422`는 비밀번호·비밀번호 확인과 인증 body의 `input`을 응답에서 제거합니다.
  SQLAlchemy engine은 debug와 무관하게 `echo=False`, `hide_parameters=True`이며, 관리자
  save summary는 11개 제한 scalar allow-list와 문자열 160자 cap만 허용합니다. password
  hash, raw `snapshot_json`, 임의 `summary_json` 키는 응답·SQL 로그에 노출하지 않습니다.
- 이번 로컬 구현에서 실제 local/Neon DB write, seed, restore, Alembic mutation,
  GitHub Actions·GHCR 게시, Render env 변경·서비스 deploy는 실행하지 않았습니다.

v370 당시 공개 회원가입 전에 별도 검토·구현 항목으로 남긴 것은 로그인·회원가입 rate limit과 실패
지연, 비밀번호 변경·분실 복구, 서버측 session/refresh·개별 token 폐기, ASGI raw body
cap, 다중 기기 save revision·충돌 해결, HTTPS/CSP/XSS, 개인정보 고지와 계정·데이터 삭제 정책입니다. 소셜 로그인은
provider-neutral 계정 연결·해제 정책을 정한 뒤 추가하며 이번 단계에는 OAuth secret이나
SDK를 만들지 않았습니다.

v377 이메일 흐름을 공개할 때는 v370 계정·캐릭터 baseline을 포함한 backend image와 legacy static을
같은 exact-SHA 승인 단위로 준비해야
합니다. `JWT_SECRET_KEY` 회전은 기존 access token을 전부 무효화하므로 노출 대응 또는
명시적인 전체 로그아웃이 필요할 때만 새 준비·배포 승인을 받아 실행합니다.

## Render GitHub App repository access — 2026-07-26

- 기호가 GitHub `Confirm access`를 완료했습니다.
- Render GitHub App은 개인 계정 `gihohoho`에서 `upgrade-rpg` 단일 저장소만 접근하도록 선택했습니다.
- 모든 저장소 접근은 허용하지 않았습니다.
- 이 확인 과정에서 새 token/PAT/secret을 문서·Git·로그에 기록하지 않았습니다.
- Static Site auto-deploy는 꺼져 있으며 승인되지 않은 commit을 자동 배포하지 않습니다.

## Secret 원칙

실제 secret 값은 적지 않습니다. token, PAT, Docker credential, production `.env`, CA/cert/key를 Git·채팅·로그·artifact에 넣지 않습니다. 나중에 사용한 credential이 생기면 사용 완료 후 회전·폐기 여부를 이 문서에 기록합니다.

## Neon database credential rotation — 2026-07-22

- Neon Free PostgreSQL 16 AWS Singapore 프로젝트 생성 직후 최초 `neondb_owner` connection string이 채팅에 노출됐습니다.
- 기호가 Neon Console에서 해당 역할 비밀번호를 즉시 재설정해 최초 credential과 connection string을 무효화했습니다.
- 노출된 값은 Git, 로컬 파일, Docker image, Render, GitHub secret에 저장하거나 사용하지 않았습니다.
- 새 direct/pooled URL은 채팅으로 받지 않고 Git/Docker 제외 경로 `deploy/.env.production`에서만 로컬 입력받습니다.
- 새 URL 입력 전까지 Neon 연결 검사, DB 생성, schema/data write, migration을 실행하지 않았습니다.
- 새 URL은 Git/Docker 제외 로컬 파일에 입력했고 Direct/Pooler 모두 TLS 1.3 인증서·호스트 검증과 read-only transaction을 통과했습니다.
- sanitized evidence에는 endpoint·URL·password를 기록하지 않았고 DB write·create, schema change, restore, Alembic은 실행하지 않았습니다.

## Production deployment approval boundary

- 운영 배포 계획 검토는 완료했지만 production host/DB/CA/proxy/domain/secret/network/rollback 입력이 미확정이므로 approval ready는 `false`입니다.
- 개인 비공개 저장소의 environment에는 native required reviewer가 없고 admins can bypass가 `true`이므로 실제 deploy 준비 commit의 정확한 SHA를 source-controlled owner approval로 다시 확인합니다.
- 실제 값은 Git 밖의 승인된 secret/deployment platform에만 넣고 final Compose render 결과에도 secret을 출력하지 않습니다.
- 첫 배포는 이전 production image가 없으므로 실패 시 proxy route를 철회하고 새 backend만 중지합니다. DB, CA, network, volume은 보존합니다.
- DB/Alembic mutation, `docker compose down -v`, 자동 retry/deploy는 승인 범위 밖입니다.

## Render application secrets — v346

- 2026-07-26에 Render용 `JWT_SECRET_KEY`와 `ADMIN_WRITE_DEV_KEY`를 로컬 CSPRNG로 각각 생성했습니다.
- 두 값은 서로 다르고 43자 이상이며 Git/Docker 제외 `deploy/.env.production`에만 있습니다.
- Neon direct URL에서 query 없는 SQLAlchemy `postgresql+asyncpg` `DATABASE_URL`을 만들었고 endpoint·role·password 일치를 값 출력 없이 검사했습니다.
- 실제 값은 Git, 문서, 채팅, 로그, artifact에 기록하지 않았고 Render에도 아직 주입하지 않았습니다.
- 승인된 v346 exact SHA로 Render secret store에 3개 secret을 전달했고 값은 화면·로그·evidence에 출력하지 않았습니다.
- 첫 deploy가 Live인 뒤 `/api/v1/health/db`를 한 번 확인했으며 credential 값은 응답이나 로그에 나타나지 않았습니다.
- 값이 노출되거나 Render 계정 접근이 의심되면 JWT/admin key를 새로 생성해 Render에 교체하고 서비스를 한 번 재배포합니다. Neon credential은 Neon Console에서 별도로 회전합니다.

## Render GHCR credential rotation — v338

- Render workspace는 `Hobby (legacy)`이고 payment method가 없습니다.
- 기존 GitHub CLI OAuth token을 Render에 저장하지 않습니다.
- dedicated classic PAT note는 `render-upgrade-rpg-ghcr-read`, scope는 `read:packages` only, 만료일은 2027-07-23입니다.
- `repo`, `write:packages`, `delete:packages`는 허용하지 않습니다.
- token 생성·Render 저장·exact-digest `Connect`는 사용자 action-time 승인을 받아 2026-07-23에 실행했습니다.
- 첫 PAT는 브라우저 검사 출력에 노출된 것을 감지했습니다. Render에는 저장하지 않았고 즉시 GitHub에서 폐기했습니다. 값은 이 문서에 기록하지 않습니다.
- 교체 PAT는 화면·로그·파일 출력 없이 Render `upgrade-rpg-ghcr-read` credential로 직접 전달했습니다.
- verified exact digest `Connect`는 성공했고 서비스 설정 화면까지 진입했습니다.
- Web Service, env secret, payment method, deploy는 생성·주입·변경·실행하지 않았습니다.
- credential은 Render에서 실제 private GHCR pull이 더 이상 필요 없거나 2027-07-23 이전 회전 시 폐기합니다.

## GitHub gate 상태

2026-07-22T12:49:50Z live API 재확인:

- external action allowlist와 full-length SHA enforcement 정상
- GitHub-owned/verified creator blanket false
- default `GITHUB_TOKEN`: contents/packages read-only
- Actions PR create/approve false
- fork write token와 secret 전달 false
- `ghcr-production-publish`: main-only, secrets 0, variables 0
- required reviewer/prevent self-review: 비공개 개인 저장소 제약으로 unavailable
- environment admins can bypass: true

따라서 owner-only source-controlled two-step을 사용합니다. `run_attempt=1`, single dispatch, immediate closure, 정확한 `closureCommitSha`, rerun 금지를 유지합니다.

### v342 v341 image 게시와 gate closure — 2026-07-26

- owner 승인 preparation: `fb231afa5081f5bfd7b459081a58bc5acd6699df`
- authorization / immediate closure / evidence: `f5d69c1bbef101cc9124b9dede18c844ef80b59c` / `ebb5ef46e3115bc358d62d93a64002b8711f4232` / `cf9e0bab121186d2ac51f889f807348cc46f192c`
- workflow run `30180738530`, `run_attempt=1`, actor `gihohoho`, conclusion `success`
- artifact IDs `8625485901`, `8625478503`; exact digest `sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1`
- local/registry Trivy HIGH·CRITICAL 0건, SLSA provenance/SPDX SBOM, Cosign OIDC sign/verify를 확인했습니다.
- lifecycle은 `attempt-recorded`, gate `false`로 닫혔고 rerun은 금지합니다.
- 실제 token 값은 출력·문서화하지 않았으며 GitHub `GITHUB_TOKEN`과 기존 Docker credential store만 사용했습니다.
- Neon restore/stamp와 Render create/deploy는 실행하지 않았고 image approval을 해당 작업에 재사용하지 않습니다.

### v341 게시 준비 lifecycle 보완 — 2026-07-26

- 승인된 `789599bfe1a26cad5d8b3d80ee6a9613c5e48576`의 lifecycle이 이전 `attempt-recorded`라 workflow의 preparation-parent 조건을 충족하지 못했습니다.
- workflow를 dispatch하지 않았고 GHCR login/build/push도 새로 실행하지 않았습니다.
- 이전 성공 run `29909291344`과 관련 SHA/digest/signature evidence를 다섯 번째 history로 보존했습니다.
- 새 attempt 슬롯은 `preparation-closed`, gate `false`, approval `null`, `not-dispatched`로 초기화했습니다.
- focused 보완 commit의 새 exact SHA 승인 전에는 authorization을 열거나 workflow를 실행하지 않습니다.

## 최신 evidence

- approved preparation `b35dfacf427162b348a6bd29eb030778edc7741c`
- authorization/closure/record `04e002060e576f19f4d8687b33635a414486206d` / `64e5ae0f5e5385ba00df16bb10ac33789ca3760a` / `303a2ed01c69c29894efdcde4ead6c2291c3d8bc`
- run `29883012957`: validation/build/SBOM 성공 후 Trivy에서 failure
- vulnerability 27건: Debian HIGH 18, CRITICAL 6, Python HIGH 3
- artifact `8515504259`, SHA-256 `6a5dfd4cd96754fd365323c7c6a7d1edf18542b5e5729e44220d7bf21ace4c50`, 만료 `2026-08-05T01:26:39Z`
- publish skipped: login/push/provenance/Cosign 미실행, registry mutation 없음

## v328 보안 준비

- Alpine 3.23 exact linux/amd64 digest와 musllinux binary-only hash lock을 채택했습니다.
- 최종 runtime에서 pip/setuptools/wheel/ensurepip과 사용되지 않는 JWT 의존성을 제거했습니다.
- 로컬 Trivy 0.70의 `--ignore-unfixed=false` HIGH/CRITICAL gate는 0건으로 통과했습니다.
- gate 완화나 예외 추가는 하지 않았고 새 workflow도 실행하지 않았습니다.
- 새 preparation SHA 승인 뒤 authorization 직전에 GitHub live 설정을 4시간 이내 기준으로 다시 확인합니다.

## 4차 run 보안 결과

- 2026-07-22T02:37:10Z allowlist/full SHA/default read-only/fork token·secret false/environment main-only를 재확인했습니다.
- GHCR login과 push가 실행되어 digest `sha256:6e4aefad0cdf1767670b7f736477dd9e00f17bf49a03fa471828df6667c41149`가 존재합니다.
- provenance/SBOM은 존재하지만 SLSA v1 경로 검사 실패로 exact-digest Trivy와 Cosign이 실행되지 않았습니다.
- unsigned·미검증 digest는 production reference에 넣거나 deploy하지 않습니다.
- workflow의 `SLSA.buildType` 검사만 `SLSA.buildDefinition.buildType`으로 바꾸는 focused fix가 후보입니다.

현재 필요한 extension·설치는 없습니다. `gh` keyring의 기존 계정 token은 만료 상태지만 Windows Git 자격 증명을 명령별 `GH_TOKEN`으로만 사용해 `repo`/`workflow` 작업을 완료했고 token 값을 저장·출력하지 않았습니다. 이 token에는 `read:org`와 `read:packages`가 없지만 현재 evidence 기록에는 필요하지 않습니다. 나중에 로컬에서 GHCR package metadata를 직접 조회해야 할 때만 `read:packages` 권한을 요청합니다.

## v330 preparation 보안 상태

- 4차 run의 login/push/digest 증거를 lifecycle history에 보존했습니다.
- 새 lifecycle은 `preparation-closed`, gate `false`, approval `null`, not-dispatched입니다.
- provenance 검사는 `SLSA`/`buildDefinition` 객체와 `buildDefinition.buildType`을 순서대로 fail-closed 확인합니다.
- workflow source/semantic/per-step SHA-256 잠금을 새 내용으로 갱신했습니다.
- 새 exact preparation SHA 승인 전에는 authorization, workflow, GHCR login/push를 실행하지 않습니다.

## v331 verified candidate 보안 결과

- 2026-07-22T09:41:21Z repository Actions/allowlist/full SHA/default token/fork/environment 설정을 재확인했습니다.
- run `29909291344`의 exact-digest Trivy 결과는 0건이고 SLSA v1 provenance/SBOM 검사가 통과했습니다.
- Cosign keyless sign/verify와 certificate identity/issuer 검증이 성공했습니다.
- verified digest는 `sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2`입니다.
- production reference, local pull, container 시작, deploy는 미실행이며 별도 승인 전에 실행하지 않습니다.

## v332 production reference 정적 준비

- `deploy/production.env.example`의 `BACKEND_IMAGE`는 검증된 exact digest로 고정했습니다.
- checker는 tag, placeholder, 다른 digest로 바뀌면 fail-closed합니다.
- 실제 secret·managed DB 주소·provider CA·network 값은 계속 placeholder입니다.
- reference는 runtime에 적용하지 않았고 Docker pull·container 시작·deploy도 실행하지 않았습니다.

## v333 local GHCR credential과 isolated 검증

- 기호가 `gihohoho` 계정으로 GitHub CLI 웹 로그인을 완료했고 OAuth scope `read:packages`를 확인했습니다.
- token 값은 출력·파일·Git·채팅·artifact에 기록하지 않고 `gh auth token | docker login ... --password-stdin`으로 Docker credential store에 전달했습니다.
- private GHCR exact digest pull과 isolated container 검증은 성공했습니다.
- 임시 container/network/local image는 제거했지만 GitHub CLI keyring과 Docker credential store의 GHCR 로그인은 남아 있습니다.
- 로컬 GHCR 접근이 더 이상 필요 없을 때 `docker logout ghcr.io`와 필요 시 `gh auth logout -h github.com -u gihohoho`를 별도 보안 정리 단계로 검토합니다. 지금 임의 logout하면 다음 승인 작업을 방해할 수 있어 자동 실행하지 않았습니다.
- 비활성 `konghjin` 계정의 만료 keyring 항목은 이번 작업에서 사용하거나 삭제하지 않았습니다.
- production secret/CA/cert/key, 실제 DB, production network는 사용하지 않았습니다.

## v352 v351 backend image 게시 준비 게이트 — 2026-07-26

- GitHub Actions repository 설정은 selected actions, full-SHA 고정, 기본 read 권한, fork write token·secret 차단 상태를 read-only로 재확인했습니다.
- `ghcr-production-publish` environment는 `main` custom branch policy를 유지하며 secret·variable은 0개입니다.
- 개인 비공개 저장소 제약상 native required reviewer가 없으므로 source-controlled exact-SHA owner approval을 계속 사용합니다.
- v341 성공 게시 run `30180738530`은 여섯 번째 `attemptHistory` 항목으로 보존했습니다.
- 현재 v351 게시 lifecycle은 `preparation-closed`, gate `false`, approval `null`, `not-dispatched`입니다.
- v352 준비 SHA 승인 전에는 workflow dispatch, GHCR mutation, Docker isolated 실행, Render deploy를 하지 않습니다.
- 승인 후에도 범위는 backend image 1회 게시와 SBOM·Trivy·provenance·Cosign·isolated 검증까지입니다. Render backend exact-image와 frontend static 배포는 새 digest 확인 뒤 별도 exact-SHA 승인을 받습니다.
- 실제 token/PAT/secret 값은 조회 결과, 문서, Git, 로그, artifact에 기록하지 않았습니다.

## v353 v351 backend image 게시·isolated 완료 — 2026-07-27

- 승인 preparation `b48dfd0751b12b1b3afb6474f9d35359ba2f8177`을 authorization `7578eb665c03ee0fcb9399929328ce684cdd1b31`에서 정확히 사용했습니다.
- workflow run `30226905547`은 run_attempt=1, actor `gihohoho`, conclusion `success`이며 같은 authorization SHA의 추가 run은 없습니다.
- gate는 run 접수 직후 closure `5d547126322dbe3c235e855cc9c2f7337342ae36`에서 닫혔고 evidence `5c842deec6d1f496679a144897f485b07428810b`에 최종 결과를 기록했습니다.
- exact digest `sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac`은 Trivy HIGH·CRITICAL 0, SLSA provenance, SPDX-2.3 SBOM, Cosign OIDC sign/verify를 통과했습니다.
- private GHCR pull과 isolated non-root/read-only/internal-network runtime 검증 후 임시 container/network/local image를 제거했습니다. 기존 PostgreSQL은 healthy입니다.
- 실제 token/PAT/secret/격리용 환경값은 Git·문서·채팅·artifact에 기록하지 않았습니다.
- Render backend/static deploy, DB/Alembic/admin write, 콘텐츠 변경은 실행하지 않았습니다.
- 다음 provider release는 별도 v354 준비 commit의 정확한 SHA 승인을 요구합니다.

## v355 Render deploy hook 회전 — 2026-07-27

- Render backend와 Static Site 설정 화면이 마스킹된 deploy hook 값을 브라우저 검사 출력에 포함하는 것을 감지했습니다.
- 두 값은 Git·파일·정제 evidence에 저장하거나 deploy에 사용하지 않았습니다.
- backend deploy hook과 Static Site deploy hook을 각각 즉시 재발급해 검사 출력에 포함된 이전 값을 폐기했습니다.
- 재발급된 새 값은 조회·복사·기록하지 않았습니다.
- hook 재발급으로 추가 deploy는 발생하지 않았습니다.
- 관련 sanitized evidence: `deploy/review/render-v351-provider-release-v355.json`
