# Current Status — v400

이 문서는 현재 구현과 승인 경계를 설명합니다. 장기 작업 규칙은 루트 [AGENTS.md](../../AGENTS.md), 새 채팅의 바로 다음 행동은 [NEXT_CHAT_HANDOFF.md](../../NEXT_CHAT_HANDOFF.md)가 기준입니다.

## 상태 표식

```txt
latest: v401.legacy-live-game-improvements
strict result: legacy-live-game-improvements
next safe stage: await-user-vue-resume
local Alembic source head: v377_auth_email_public_security
local/Neon DB current: v377_auth_email_public_security / v377_auth_email_public_security
v377 apply/stamp/downgrade: local 1/0/0; Neon 1/0/0
email rollout approval/execution: yes/public-live
public backend/static: v377/v401 Live
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
v390 production approval/execution: no/no
v391 production approval/execution: no/no
v392 production approval/execution: no/no
v393 production approval/execution: no/no
v394 production approval/execution: no/no
v395 production approval/execution: no/no
v396 production approval/execution: no/no
v397 production approval/execution: no/no
v398 production approval/execution: no/no
v399 production approval/execution: no/no
v400 legacy hotfix approval/execution: yes/yes
v401 legacy improvements approval/execution: yes/yes
```

## v401 실서버 게임 편의 개선

- Vue는 중단 상태입니다. 사용자 요청 5개: 백그라운드 진행, 묶음 드랍 확률, 소환 기본 ON/다른 보스 차단, 해금 도감 능력치, 스킬 피해 공식 강조를 legacy에 적용합니다. static 배포까지 승인됐습니다.
- 경과시간 순서로 공격·버프·필드 재등장·특수보스 쿨타임을 처리합니다. 지연은 500개 이벤트씩 나누고 완료 전 입력을 잠급니다. 계정 전환/로그아웃 시 시계를 중단하며 중단 시간은 재생하지 않습니다. 화면 효과는 생략하고 최근 로그 200개를 복귀 시 표시합니다. 브라우저 종료·탭 폐기 뒤 오프라인 사냥은 지원하지 않습니다.
- 장비는 `5종 중 1개 · 8.00%`처럼 묶음 확률, 휘장은 개별 판정으로 표시합니다. 실제 확률/seed는 유지합니다. 새 소환은 자동소환·장비드랍 ON, 다른 보스 선택은 보스제거 안내로 차단합니다.
- 도감은 실제 template/+단계 능력치를 hover·클릭·키보드로 표시합니다. 모바일은 한 열입니다. 스킬 공식/최종 피해를 굵기·색으로 구분하며 현재 레벨·탈리스만·피해 증가를 반영하고 치명타는 제외합니다.
- 전체 core·JS syntax·변경 Python compileall·static build PASS. 마지막 지급 ID 충돌 보강 뒤 관련 5개 회귀도 PASS. 공개 데이터로 전경/지연·특수복귀·pause/resume·45종을 검증했습니다. 1366/390px 도감·스킬 확인, console error 0입니다.
- 2026-09-12 17:48 KST, SHA `a86fd0c2c9c31516a73cf6de352dc6f34a67851d` → deploy `dep-daih3krm8hqs73crb140` 1회 Live(16.1초). 변경 파일 7개 GET 200·Git bytes 일치, 최신 공개 API 회귀 PASS. 기존 서버 재시작 불필요.

## v400 실서버 보스 드랍 긴급 수정

- adapter가 누락한 확률 4종·제목을 raw/table에서 복원했습니다. 명시적 0·보정 marker를 보존하고 adapter 캐시는 v400입니다. 확률·seed·backend·DB는 유지합니다.
- 2026-09-12 00:33 KST, SHA `6652e41ceb50edc077414d0b8d3a531c27b6df7f` → static `srv-d9iu337aqgkc73am4lh0`, deploy `dep-dai1u8mq1p3s73anmmi0` 1회 Live. rollback 기준입니다. 전체 core·build PASS, 공개 bytes 일치 및 45종/245개 지급·화면 검증 PASS입니다.

## v399 가방↔보관함 이동·정렬 저장

- 묶음 이동은 첫 빈 칸, 정렬은 상대 순서를 유지하며 ID·강화·수량·추가 필드를 보존합니다. prospective 복구본 기록 후 공통 queue에 저장하고, quota/다른 탭은 변경 전 차단합니다. 실패 pending의 재시도는 이동을 반복하지 않습니다.
- 전체 Vue smoke·TypeScript·build 및 1366/390px 이동·정렬·503 재시도·pending·overflow/console 0 PASS. 장착·사용·판매·자동 합치기·휴지통 write·Gold·보상·backend·DB·배포는 미변경입니다. 다음 Vue 단계는 자동 합치기이며 사용자 재개까지 보류합니다.

## v396~v398 보유 표시·복구·가독성

- v398은 가방·15칸 장비·보관함·휴지통과 좌우 창에 실제 보유 snapshot을 표시합니다. 빈 칸·ID·강화·수량·등급·미등록 항목을 보존하며 원래 container/index로 선택을 구분합니다. 저장소 PNG만 hash URL로 번들링합니다.
- v397은 계정/슬롯/캐릭터별 snapshot·pending·백업을 기록합니다. local/server/취소 선택 전에는 boot·자동 저장을 시작하지 않습니다. 늦은 응답은 최신 pending을 지우지 않습니다. 상세 키·실패 계약은 [계정·저장 계약](ACCOUNT_AUTH_AND_CHARACTER_SLOTS.md)을 따릅니다.
- v396의 13px typography·명암·좌우 창과 공유 modal 접근성, 관리자 helper 정리와 terminal save barrier를 유지합니다. v396~v398 Vue smoke/build·1366px/390px synthetic 브라우저 검사는 PASS했습니다.

## v384~v395 이전 Vue 기반

- [typed domain 의존성](../generated/VUE_GAME_DOMAIN_DEPENDENCIES.md)과 마을/HUD·필드·보스·스킬·상점·설정 표시를 이식했습니다. snapshot load 성공 뒤 단일 전투 timer가 시작되지만 HP·Gold·아이템 보상·난수·cooldown은 저장하지 않습니다.
- GET/POST는 Bearer·슬롯·캐릭터 identity를 검사합니다. 자동 60초·수동·전환 저장은 한 queue를 사용하며 최종 저장 성공 뒤 선택/token을 정리합니다. `saveVersion`은 형식 버전이고 backend CAS는 미구현입니다. 상세는 [계정·저장 계약](ACCOUNT_AUTH_AND_CHARACTER_SLOTS.md)을 따릅니다.
- smoke/build와 후속 v396 브라우저 검사가 PASS했습니다. 이전 구현 상세는 [Vue 전환 계획](../reference/frontend/VUE_FASTAPI_DB_TRANSITION_PLAN.md)과 Git 이력을 따릅니다.

## v378 게임 UI·환경 라우팅 소스 준비

- SQ·SW 첫 전용 강화권은 저장·표시·전투 모두 `Lv.1`이고 탈리스만 A/B 보너스를 상속하지 않습니다. `접속 캐릭터` 바는 `town`에서만 표시합니다.
- 배포 origin의 테스트 UI는 로그인한 관리자에게만 보이며 로컬 개발 편의는 유지합니다. 이 화면 gate와 별개인 server save 검증/CAS는 남아 있습니다.
- 로컬 API는 `127.0.0.1:8000/api/v1`, 배포는 Render API로 고정해 stale `8001`의 `Failed to fetch`를 복구했습니다. dev key는 ignored dotenv에만 있고 로그인 가능한 production `admin`은 현재 관리자가 아닙니다.
- v378 SHA `c56525394a4099160e7a32e93dc2d3a0d54568b3` / deploy `dep-da5vn3m417fc738rs2bg`는 v400 이전 배포이며 rollback 기준입니다.

## v377 구현과 환경

- `auth_rate_limit_buckets`는 원문 identity 대신 HMAC digest를 저장하며 row lock, fixed window와 cooldown을 적용합니다. auth 9개 POST는 JSON 파싱 전 신뢰 IP 확인과 16,384-byte body cap을 거치고 `Cache-Control: no-store`를 유지합니다.
- durable outbox/queue `auth_email_outbox`는 수신자·원문 token·본문 없이 HMAC 대상과 단일 시도 상태만 보존합니다. worker는 `FOR UPDATE SKIP LOCKED`로 claim하며 provider 시작 건을 자동 재시도하지 않습니다.
- 인증 재전송·아이디 찾기·재설정은 실제·decoy 모두 generic 202로 account enumeration을 막고, 조건을 만족한 7일 초과 미인증 계정만 재가입에서 회수합니다. frontend는 202·429·413와 stable auth code를 처리합니다.
- private ACL과 local/production 분리 secret을 준비했고 `email-validator==2.3.0`·`dnspython==2.8.0`을 Linux runtime/musllinux/dev lock에 고정했습니다. local Brevo의 Naver 수신→링크 인증→로그인→8개 슬롯 E2E를 확인했습니다.

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
- v377 당시 legacy static deploy `dep-da4qr867bikc73aekck0`은 후속 v378 `dep-da5vn3m417fc738rs2bg`로 교체됐습니다. 현재 v400 배포 여부는 위 긴급 수정 절을 따릅니다.
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

1. `await-user-vue-resume`: 보스 드랍 수정·배포 완료. Vue 후속 `migrate-vue-game-stack-merge-foundation`은 사용자 재개 요청까지 보류합니다.
2. 실제 관리자 Apply API·재인증·dev key header·DB write 연결은 이번 단계에 포함되지 않았습니다. 필요하면 작업 종류와 정확한 DB-write 범위를 별도 승인받습니다.
3. production 관리자 복구는 별도 guarded recovery와 exact DB-write 승인을 받기 전까지 실행하지 않습니다.

## 배포 주소

- 공개 frontend: `https://gihohoho-upgrade-rpg.onrender.com/index.html`, `/admin.html`
- 공개 backend: `https://upgrade-rpg-api.onrender.com`
- GHCR repository: `ghcr.io/gihohoho/upgrade-rpg-backend`, target `linux/amd64`
- 상세 인증 계약은 [이메일 인증·복구·삭제](ACCOUNT_EMAIL_VERIFICATION_RECOVERY_AND_DELETION.md), 저장 계약은 [계정·캐릭터 슬롯](ACCOUNT_AUTH_AND_CHARACTER_SLOTS.md), 후속 gate는 [Security Gates](SECURITY_ROTATION_AND_GITHUB_GATES.md)를 따릅니다.
