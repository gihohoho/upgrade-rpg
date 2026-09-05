# Current Status — v395

이 문서는 현재 구현과 승인 경계를 설명합니다. 장기 작업 규칙은 루트 [AGENTS.md](../../AGENTS.md), 새 채팅의 바로 다음 행동은 [NEXT_CHAT_HANDOFF.md](../../NEXT_CHAT_HANDOFF.md)가 기준입니다.

## 상태 표식

```txt
latest: v395.vue-game-serialized-save-queue-foundation
strict result: vue-game-serialized-save-queue-foundation
next safe stage: migrate-vue-game-pending-unsynced-recovery-foundation
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
v390 production approval/execution: no/no
v391 production approval/execution: no/no
v392 production approval/execution: no/no
v393 production approval/execution: no/no
v394 production approval/execution: no/no
v395 production approval/execution: no/no
```

## v395 선택 캐릭터 단일 직렬 저장 queue 기반

- typed `POST /api/v1/game/save` client가 현재 Bearer token, `character-N`, 32자리 `accountCharacterId`와 호출 시점의 detached server state를 한 요청으로 고정합니다. snapshot은 기존 `createServerSavePayload`로 만들고 Gold·레벨·최근 구역과 item container count만 summary allow-list에 담습니다.
- 자동 60초 저장, 마을의 수동 저장, 캐릭터 전환·로그아웃 전 최종 저장은 모두 실패한 앞 요청이 뒤 요청을 막지 않는 하나의 Promise 직렬 queue를 사용합니다. 전환은 runtime을 먼저 pause하고 앞선 queue와 마지막 저장을 기다린 뒤 성공할 때만 캐릭터 선택이나 token을 정리합니다.
- 응답의 type·data·payload에서 슬롯·캐릭터 ID·캐릭터 종류·saveVersion을 다시 대조합니다. 401/403은 로그인 만료, 409는 자동 덮어쓰기와 후속 자동 저장을 멈추는 conflict, network/timeout/429/5xx는 token·선택을 유지하는 retryable 오류, 413/422와 응답 불일치는 contract 오류로 분리합니다.
- backend의 현재 `saveVersion`은 snapshot 형식 버전이며 다중 기기 CAS revision이 아닙니다. Vue가 `expectedRevision`을 임의로 만들거나 409를 자동 재시도하지 않으며 실제 CAS schema/API는 공개 확대 전 별도 backend 단계로 남깁니다.
- 저장 adapter·queue·Pinia 실행·자동/수동/전환 gate focused smoke, 전체 Vue shell smoke, TypeScript 검사와 production build가 PASS했습니다. 실제 DB save POST는 실행하지 않았고 backend·DB·env·secret·legacy·Render·production 배포도 변경하지 않았습니다. Chrome·확장·native host 설치 상태는 정상이었지만 이번 실행의 제어 연결이 끊겨 mock fixture 브라우저 조작은 완료하지 못했고 fixture는 제거했습니다.

## v394 선택 캐릭터 server snapshot read/load 기반

- 캐릭터 선택 뒤 `GamePlayShell`이 Bearer token, `character-N`, 32자리 `accountCharacterId`로 `GET /api/v1/game/load`를 호출합니다. 응답 envelope와 payload의 슬롯·캐릭터 ID·캐릭터 종류를 현재 선택과 다시 대조하고 일치할 때만 typed server state로 normalize/apply합니다.
- 신규 캐릭터의 빈 `{}` snapshot은 서버 연결 실패가 아니라 정상 기본 상태로 처리합니다. 기존 snapshot은 Gold·레벨·상세 능력치·스킬·최근 구역에 반영되고 필드·보스의 기본 공격 계산에도 같은 읽기 상태를 전달합니다.
- load 전에는 전체 게임 대신 명시적 로딩 화면을 표시합니다. network/timeout/429/404/5xx와 계약 불일치는 token과 선택 캐릭터를 유지한 오류 화면에서 다시 불러오기/캐릭터 재선택을 제공하며, 401/403만 session을 폐기하고 로그인으로 돌아갑니다. 새 요청과 component 해제는 이전 GET과 client timer를 정리합니다.
- API와 adapter/store focused smoke, 전체 Vue shell smoke와 production build를 통과했습니다. v394 당시에는 save POST·자동/수동/전환 저장을 연결하지 않았으며 local fallback·pending-unsynced 충돌 해결·Gold/아이템 보상·난수·CAS revision은 지금도 연결하지 않았습니다.

## v393 빈 게임 화면 복구·client 전투 runtime 기반

- snapshot load 성공 뒤에만 독립 `combatRuntime`이 단일 timer로 client-only 전투를 수행합니다. 대상 전환·마을 복귀·component 해제에서 timer를 정리하고 pause 원인을 분리합니다.
- 이 runtime은 v394 snapshot을 읽고 v395 queue가 typed server state를 저장하지만 client 전투 HP, Gold·아이템·보상·난수·cooldown·자동 재등장/재소환을 server state에 쓰지 않습니다. 당시 desktop/mobile fixture와 focused smoke가 PASS했습니다.

## v384~v392 이전 Vue 게임 기반

- v384는 legacy game JavaScript의 의존성을 [자동 생성 보고서](../generated/VUE_GAME_DOMAIN_DEPENDENCIES.md)로 고정하고 state/save·slot·전투 규칙·action result를 순수 TypeScript로 분리했습니다.
- v385~v387은 마을 전용 접속 캐릭터 바·HUD와 master-data 필드·보스 표시 UI를, v388~v389는 15개 장비·24개 가방 및 보관함·휴지통의 빈 칸·독립 정렬 규칙을 이식했습니다.
- v390은 스킬 10단계와 강화 규칙, SQ·SW 첫 Lv.1·보너스 비상속, 탈리스만/휘장 `2^현재 강화` 재료를 표시합니다.
- v391은 구매 계약을 만들지 않는 master-data 가격 카탈로그와 저장 없는 설정 preview, v392는 legacy형 좌우 창·utility/mobile modal·최소 12px 가독성을 완성했습니다.
- 각 단계의 desktop/mobile·focused smoke가 PASS했습니다. 이후 v393 client HP timer와 v394 load, v395 snapshot save queue만 추가했으며 Gold·보상·쿨타임·아이템/스킬 변경·난수와 backend·DB·legacy·Render는 바꾸지 않았습니다.

## v378 게임 UI·환경 라우팅 소스 준비

- SQ·SW 첫 전용 강화권은 저장·표시·전투 모두 `Lv.1`이고 탈리스만 A/B 보너스를 상속하지 않습니다. `접속 캐릭터` 바는 `town`에서만 표시합니다.
- 배포 origin의 테스트 UI는 로그인한 관리자에게만 보이며 로컬 개발 편의는 유지합니다. 이 화면 gate와 별개인 server save 검증/CAS는 남아 있습니다.
- 로컬 API는 `127.0.0.1:8000/api/v1`, 배포는 Render API로 고정해 stale `8001`의 `Failed to fetch`를 복구했습니다. dev key는 ignored dotenv에만 있고 로그인 가능한 production `admin`은 현재 관리자가 아닙니다.
- 승인 SHA `c56525394a4099160e7a32e93dc2d3a0d54568b3`의 v378 legacy static은 Render deploy `dep-da5vn3m417fc738rs2bg`로 1회 배포되어 live이며 backend·DB·secret은 바꾸지 않았습니다.

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

1. `migrate-vue-game-pending-unsynced-recovery-foundation`: 서버 저장 실패 때 계정·캐릭터별 local fallback과 `pending-unsynced` marker를 보존하고, 재진입 시 local/server/취소를 사용자가 명시적으로 선택하는 복구 gate를 Vue에 이식합니다. Gold/아이템 보상·난수 드랍과 자동 충돌 선택은 함께 연결하지 않습니다.
2. 실제 관리자 Apply API·재인증·dev key header·DB write 연결은 이번 단계에 포함되지 않았습니다. 필요하면 작업 종류와 정확한 DB-write 범위를 별도 승인받습니다.
3. production 관리자 복구는 별도 guarded recovery와 exact DB-write 승인을 받기 전까지 실행하지 않습니다.

## 배포 주소

- 공개 frontend: `https://gihohoho-upgrade-rpg.onrender.com/index.html`, `/admin.html`
- 공개 backend: `https://upgrade-rpg-api.onrender.com`
- GHCR repository: `ghcr.io/gihohoho/upgrade-rpg-backend`, target `linux/amd64`
- 상세 인증 계약은 [이메일 인증·복구·삭제](ACCOUNT_EMAIL_VERIFICATION_RECOVERY_AND_DELETION.md), 저장 계약은 [계정·캐릭터 슬롯](ACCOUNT_AUTH_AND_CHARACTER_SLOTS.md), 후속 gate는 [Security Gates](SECURITY_ROTATION_AND_GITHUB_GATES.md)를 따릅니다.
