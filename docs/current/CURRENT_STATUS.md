# Current Status — v389

이 문서는 현재 구현과 승인 경계를 설명합니다. 장기 작업 규칙은 루트 [AGENTS.md](../../AGENTS.md), 새 채팅의 바로 다음 행동은 [NEXT_CHAT_HANDOFF.md](../../NEXT_CHAT_HANDOFF.md)가 기준입니다.

## 상태 표식

```txt
latest: v389.vue-game-storage-trash-ui-foundation
strict result: vue-game-storage-trash-ui-foundation
next safe stage: migrate-vue-game-skill-enhancement-ui-foundation
local Alembic source head: v377_auth_email_public_security
local/Neon DB current: v377_auth_email_public_security / v377_auth_email_public_security
v377 apply/stamp/downgrade: local 1/0/0; Neon 1/0/0
email rollout approval/execution: yes/public-live
public backend/static: v377/v378 Live
production approval/execution: yes/yes
v378 production approval/execution: yes/yes
v379 production approval/execution: no/no
v380 production approval/execution: no/no
v381 production approval/execution: no/no
v382 production approval/execution: no/no
v383 production approval/execution: no/no
v384 production approval/execution: no/no
v385 production approval/execution: no/no
v386 production approval/execution: no/no
v387 production approval/execution: no/no
v388 production approval/execution: no/no
v389 production approval/execution: no/no
```

## v389 보관함·휴지통 UI 기반

- 순수 adapter가 보관함·휴지통을 각각 20개 표시 슬롯과 60칸 계약으로 만들고, 두 공간의 첫 빈 칸과 상대 순서 보존 정렬을 독립적으로 계산합니다. source 입력은 바꾸지 않습니다.
- 선택과 두 `위로 정렬 미리보기`만 화면 상태를 바꿉니다. 가방/보관함 이동·휴지통 이동/복구·영구 삭제·snapshot·save는 잠겨 있습니다.
- 마을 왕복·접속 캐릭터 바 비노출·각 20슬롯·정렬 전후 첫 빈 칸 2/7번·선택 유지·독립 정렬·desktop/mobile 4열·가로 넘침 없음·Vite error overlay 0과 focused smoke가 PASS했습니다. backend·DB·legacy·Render·배포는 바꾸지 않았습니다.

## v386~v388 이전 Vue 게임 UI

- v386~v387은 `baseUrl` 제거와 master-data 필드·보스의 표시 전용 전투 UI를, v388은 15개 장비·24개 가방 슬롯과 첫 빈 칸·상대 순서 보존 정렬을 이식했습니다.
- 실제 HP·골드·보상·쿨타임·장착·사용·판매·강화·이동·save·timer·난수는 바꾸지 않았고 각 desktop/mobile·focused smoke가 PASS했습니다.

## v385 마을·HUD

- 캐릭터 선택 뒤 마을에서만 접속 캐릭터 바·시설·HUD·능력치·스킬을 표시합니다. 슬롯의 이름·레벨·골드·최근 구역과 아직 load하지 않은 domain 능력치를 구분합니다.
- 미연결 기능은 접근 가능한 안내 modal만 엽니다. snapshot load/save·자동 저장·전투 timer와 backend·DB·legacy·Render는 변경하지 않았습니다.
- adapter/Pinia 경계, desktop/mobile·modal·가로 넘침·console, Vue build·focused smoke가 PASS했습니다.

## v384 Vue game domain 기반

- legacy game JavaScript 8개/3,481줄의 browser·runtime 의존성을 [자동 생성 보고서](../generated/VUE_GAME_DOMAIN_DEPENDENCIES.md)로 고정했습니다.
- state/save·slot·전투 규칙·action result를 순수 TypeScript로 분리했고 legacy 동등성 검사가 PASS했습니다.
- snapshot load/save·전투 timer와 legacy·backend·DB·Render는 바꾸지 않았습니다.

## v378 게임 UI·환경 라우팅 소스 준비

- SQ·SW의 첫 전용 강화권은 저장·화면·전투 계산에서 모두 `Lv.1`입니다. 탈리스만 A/B는 더 이상 SQ·SW에 합산되지 않으며 R·T / F·D 보너스만 유지합니다. 브라우저 source와 generated skill seed, 탈리스만 설명도 동기화했습니다.
- `접속 캐릭터` 바는 `town`에서만 표시하고 필드·보스·초기 상태에서는 hidden/inert로 닫습니다.
- 배포 origin의 테스트 패널·지급 모달·MASTER DATA/SAVE DATA 개발 배지는 현재 로그인 사용자가 관리자일 때만 표시합니다. 로컬 개발 origin은 기존 테스트 편의를 유지합니다. 이 UI gate는 server-authoritative anti-cheat 경계가 아니며 그 범위는 save revision/CAS와 함께 남아 있습니다.
- 로컬 API는 `127.0.0.1:8000/api/v1`, 배포 API는 Render 주소로 고정합니다. stale production URL과 stale local port를 무시하며 배포 관리자 페이지의 API `기본값` 버튼도 배포 주소를 유지합니다.
- 실제 브라우저에서 로컬 stale `8001` 실패를 확인하고 수정 뒤 `Failed to fetch` 대신 로컬 backend의 정상 인증 오류 응답이 표시되는 데까지 검증했습니다.
- local/Neon의 `local-dev` legacy 관리자 row는 password가 없어 로그인할 수 없습니다. production의 로그인 가능한 `admin` 계정은 관리자 권한이 없습니다. 두 환경의 dev key는 private ignored dotenv에만 있으며 값은 보고하지 않습니다.
- 승인 SHA `c56525394a4099160e7a32e93dc2d3a0d54568b3`의 v378 legacy static은 Render deploy `dep-da5vn3m417fc738rs2bg`로 정확히 1회 배포되어 live입니다. 298개 파일 build와 secret 미포함, public index/admin·핵심 v378 자산 HTTP 200, 미로그인 테스트 패널 denied/hidden을 확인했습니다. backend·DB·secret은 변경하지 않았습니다.

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

- 최초 v377 publish preparation `d58d093fc5ac2a4ffefa812e7067cb3083ce8a7d`와 GitHub Actions run `32576889295`는 기본 email/security image를 게시했습니다. 메일 finalize fix는 별도 preparation `cd357de032425138d44323dd3060bbbf5b6a45d8`과 GitHub Actions run `32587614153`, `run_attempt=1`로 게시했고 rerun하지 않았습니다.
- 현재 production image는 `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:80e8f57618b2bd8bbac37fd63381e454434e06b67eff0cd8f4327796bdc1c677`입니다.
- Render backend service에는 email/security 환경변수 35개를 key-name-only로 확인하고 secret 값 노출 없이 저장했습니다. deploy `dep-da4tp7nqj5pc73b6l910`은 현재 digest로 live입니다.
- legacy static deploy `dep-da4qr867bikc73aekck0`은 commit `ceea14c20ac8604d453930d8f6c5127f00236352`를 build해 live입니다.
- 공개 backend health는 HTTP 200입니다. 공개 인증 POST는 schema-invalid 요청에 422, 허용된 Naver 테스트 주소의 인증메일 재요청에 generic 202 accepted를 반환했고 두 응답 모두 `Cache-Control: no-store`였습니다.
- 이전 `auth_protection_unavailable`과 “이메일 보안 설정이 아직 준비되지 않았습니다” 503은 공개 경로에서 재현되지 않습니다.
- production 메일 장애의 첫 원인은 Brevo Authorized IP가 Render shared outbound IP를 허용하지 않은 것이었습니다. Render 공식 CIDR `74.220.52.0/24`, `74.220.60.0/24`를 등록한 뒤 실제 인증 메일이 provider에서 Delivered로 확인됐습니다.
- 실제 전송 뒤 outbox가 `sending`에 남은 원인은 성공 finalize에서 `completed_at`보다 `sent`가 먼저 autoflush되어 DB CHECK 제약을 위반한 것이었습니다. `de3ae5d`가 필드 설정 순서를 고치고 fake autoflush 회귀를 추가했습니다.
- fix publish preparation `cd357de032425138d44323dd3060bbbf5b6a45d8`, authorization `46c9e7e33d866b160b6f4a8f36d5b68dabe3ece4`, immediate closure `e07474d5b5411dd805736687d1003f451298dae4`, evidence record `3e3516299a72e47c6d85597f8c0b60db5cb11a46`를 push했습니다. GitHub Actions run `32587614153`, `run_attempt=1`이 취약점 차단·SBOM·provenance·Cosign 검증을 통과해 digest `sha256:80e8f57618b2bd8bbac37fd63381e454434e06b67eff0cd8f4327796bdc1c677`를 게시했습니다.
- Render backend deploy `dep-da4tp7nqj5pc73b6l910`은 새 digest로 live이며 internal/public health가 200입니다. 배포 뒤 공개 비밀번호 재설정 요청은 202와 `no-store`, 최신 outbox/token은 1회 시도 `sent`, provider 기록 존재, 오류 없음입니다. 이미 인증된 계정의 인증메일 재전송은 의도대로 suppressed됐습니다.
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
- 공개 테스트 메일함의 2026-08-23 02:32 KST 비밀번호 재설정 메일 도착 확인
- server session/refresh/revoke, save revision/CAS, CSP/XSS·브라우저 token 정책, 개인정보 정책 구현

## 공개 전 필수 보강

v377 rate limit, durable outbox/queue, raw body cap, 미인증 계정 회수와 이메일 rollout은 공개 배포됐습니다. 공개 회원가입을 확대하기 전에는 다음이 남아 있습니다.

1. 서버측 session/refresh/revoke와 기기별 원격 폐기 정책
2. 다중 기기 save revision/CAS와 충돌 해결
3. HTTPS/CSP/XSS 회귀와 브라우저 token 저장 정책
4. 개인정보 보관·삭제·문의·복구 정책
5. 공개 이메일 delivery 관찰과 secret 회전·운영 보관 절차

## 바로 다음 단계

1. Vue 전체 전환 순서에 따라 typed skill/enhancement rule을 사용하는 스킬·강화 표시 UI를 이식합니다. 실제 스킬 사용·강화·재료 소비·snapshot load/save·자동 저장은 아직 연결하지 않습니다.
2. 실제 관리자 Apply API·재인증·dev key header·DB write 연결은 이번 단계에 포함되지 않았습니다. 필요하면 작업 종류와 정확한 DB-write 범위를 별도 승인받습니다.
3. production 관리자 복구는 별도 guarded recovery와 exact DB-write 승인을 받기 전까지 실행하지 않습니다.

## 배포 주소

- 공개 frontend: `https://gihohoho-upgrade-rpg.onrender.com/index.html`, `/admin.html`
- 공개 backend: `https://upgrade-rpg-api.onrender.com`
- GHCR repository: `ghcr.io/gihohoho/upgrade-rpg-backend`, target `linux/amd64`
- 상세 인증 계약은 [이메일 인증·복구·삭제](ACCOUNT_EMAIL_VERIFICATION_RECOVERY_AND_DELETION.md), 저장 계약은 [계정·캐릭터 슬롯](ACCOUNT_AUTH_AND_CHARACTER_SLOTS.md), 후속 gate는 [Security Gates](SECURITY_ROTATION_AND_GITHUB_GATES.md)를 따릅니다.
