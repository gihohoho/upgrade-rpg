# 계정 인증·캐릭터 슬롯·회원 관리 — v377

```txt
latest: v386.vue-game-field-combat-ui-foundation
strict result: vue-game-field-combat-ui-foundation
next safe stage: migrate-vue-game-boss-combat-ui-foundation
public Render: backend v377 / static v378 Live
local/Neon DB: v377 / v377
```

v370의 로그인·캐릭터 슬롯·관리자 회원 관리 기반과 v371 이메일 identity lifecycle을
그대로 유지합니다. v377은 그 위에 공개 인증 요청 제한, JSON 파싱 전 body cap, durable
semantic email outbox와 만료된 미인증 identity의 안전한 회수를 source로 준비합니다.
상세 이메일 계약과 Brevo 개인정보 설정은
`ACCOUNT_EMAIL_VERIFICATION_RECOVERY_AND_DELETION.md`가 기준입니다.

## 이번 단계의 목표

게임을 처음 열면 바로 플레이 화면을 시작하지 않고 다음 순서로 진입합니다.

```txt
로그인 또는 회원가입
  → 계정의 캐릭터 슬롯 8개 조회
  → 기존 캐릭터 선택 또는 빈 슬롯에 캐릭터 생성
  → 선택한 캐릭터의 저장 데이터만 로드
  → 게임 시작
```

소셜 로그인은 나중에 추가할 수 있도록 고려하되, 이번 단계에는 OAuth 공급자,
버튼, 외부 SDK와 사용하지 않는 설정을 만들지 않습니다.

## 데이터 구조

v370은 새 테이블과 Alembic revision 없이 기존 구조를 사용했습니다. v371은 기존 행을
거짓 이메일로 채우지 않으면서 신규 가입자의 이메일을 안전하게 관리하기 위해
`v371_email_identity_lifecycle` revision source를 준비했습니다. v377 source head는 그
다음 `v377_auth_email_public_security` revision이며, local/Neon DB에 각각 1회 적용했습니다.

- `users`: 아이디, nullable legacy-safe 원본/정규화 이메일, 인증 시각,
  `authVersion`, bcrypt 비밀번호 해시, 활성/정지, 관리자 여부
- `user_profiles`: 기존 계정 프로필 1:1 행
- `user_save_snapshots`: 계정별 캐릭터 슬롯과 전체 게임 저장
- `admin_change_logs`: 최초 관리자 지정과 회원 활성/정지 감사 기록
- `user_email_action_tokens`: 인증·비밀번호 재설정·계정 삭제용 일회용 HMAC digest,
  만료·사용·제한된 전달 상태
- `auth_rate_limit_buckets`: 원문 IP·이메일·아이디·token 대신 별도 secret HMAC digest로
  구분하는 PostgreSQL 요청·실패 bucket
- `auth_email_outbox`: 목적·HMAC 대상 digest·상태만 보관하는 durable semantic mail job;
  수신자 주소·원문 token·제목·본문은 저장하지 않음
- `characters`: 검신 같은 선택 가능한 **캐릭터 종류 마스터 데이터**이며 계정 슬롯이 아님

한 계정의 슬롯은 DB에서 `character-1`부터 `character-8`까지 고정합니다. 각
`user_save_snapshots.summary_json.accountCharacter`에는 다음 안전 메타데이터만
보관합니다.

```json
{
  "id": "32자리 무작위 캐릭터 고유 ID",
  "slotIndex": 1,
  "name": "사용자가 정한 이름",
  "characterCode": "weapon_master",
  "createdAt": "UTC 시각"
}
```

슬롯 번호는 재사용될 수 있지만 캐릭터 고유 ID는 다시 만들 때마다 바뀝니다.
API 요청·응답에서는 이 `summary_json.accountCharacter.id` 값을
`accountCharacterId`라는 필드명으로 전달합니다.
서버는 저장·불러오기 때 현재 로그인 계정, `character-N` 슬롯 키, 캐릭터 고유
ID가 모두 일치해야만 요청을 허용합니다. 따라서 캐릭터를 삭제한 뒤 같은 슬롯에
다시 만들어도 이전 브라우저 캐시가 새 캐릭터에 자동 연결되지 않습니다.

기존 `UserCharacterSkill`, `UserEquipmentSlot`, `ItemInstance` 같은 정규화 초안
테이블은 같은 직업 캐릭터 여러 개를 구분할 수 없으므로 이번 단계에서 이중 쓰기하지
않습니다. 캐릭터 한 명은 기존 게임 전체 save snapshot 한 개를 소유합니다.

## 인증과 비밀번호

- 회원가입 아이디는 소문자 영문·숫자·밑줄의 4~24자 규칙으로 정규화합니다.
- 회원가입은 이메일을 필수로 받고 설치·lock 반영된 `email-validator 2.3.0`으로 원본
  표기와 canonical 주소를 분리합니다. dependency가 빠지면 약한 parser로 폴백하지 않고
  이메일 동작을 fail-closed로 닫습니다.
- 비밀번호는 최소 8자, 문자와 숫자를 각각 하나 이상 포함하고 UTF-8 72바이트를
  넘지 않아야 합니다.
- 비밀번호는 `bcrypt 5.0.0`으로만 해시하며 원문과 해시는 API, 관리자 화면,
  로그, 문서에 반환하지 않습니다.
- CPU 비용이 큰 bcrypt hash/verify는 FastAPI event loop가 아니라 worker
  thread에서 실행합니다.
- 이메일 인증 전에는 access token을 발급하지 않습니다. 인증 뒤 아이디 또는 이메일과
  비밀번호로 로그인하면 기존 `JWT_SECRET_KEY`로 HS256 서명한 24시간 access token을
  발급합니다. 서버는 알고리즘을 고정하고 서명, 종류, 발급 시각, 만료 시각과 DB의 현재
  `authVersion`을 검사합니다.
- v295 이전에 만들어져 email 열이 `NULL`인 기존 계정은 기존 아이디·비밀번호 접근을
  유지합니다. 이 경우 응답은 `emailVerified=false`로 사실대로 표시하며, 이메일이 있는
  신규 계정은 링크 인증 전 계속 차단합니다.
- 로그인 유지가 꺼져 있으면 token은 `sessionStorage`, 사용자가 명시적으로 켜면
  `localStorage`에 저장합니다. 로그아웃은 클라이언트 token을 즉시 삭제합니다.
- 매 인증 요청마다 DB의 계정을 다시 읽으므로 관리자가 계정을 정지하면 이미 발급된
  token도 다음 요청부터 즉시 거절됩니다.
- 회원가입 요청으로 관리자 권한을 받을 수 없으며 항상 `is_admin=false`입니다.
- 비밀번호 재설정은 같은 transaction에서 `authVersion`을 증가시켜 기존 access token을
  전부 무효화합니다. 이메일 작업 원문 token은 DB에 저장하지 않고 별도
  `EMAIL_TOKEN_SECRET` HMAC-SHA256 digest만 저장합니다.

서버 session/refresh token 테이블은 이번 MVP에 없습니다. 따라서 개별 기기 강제
로그아웃, token 목록과 원격 폐기, refresh rotation은 아직 제공하지 않습니다.
전체 token을 무효화해야 하면 `JWT_SECRET_KEY`를 회전하고 새 backend image를
배포해야 합니다.

## API 계약

공개 경로:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/verify-email`
- `POST /api/v1/auth/resend-verification`
- `POST /api/v1/auth/recover-username`
- `POST /api/v1/auth/request-password-reset`
- `POST /api/v1/auth/reset-password`
- `POST /api/v1/auth/account-deletion/confirm`
- `GET /api/v1/game/master-data`
- health 경로

Bearer 로그인이 필요한 경로:

- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/account-deletion/preview`
- `POST /api/v1/auth/account-deletion/request`
- `GET /api/v1/account/characters`
- `POST /api/v1/account/characters`
- `DELETE /api/v1/account/characters/{account_character_id}`
- `GET /api/v1/game/load`
- `GET /api/v1/game/save-slots`
- `POST /api/v1/game/save`

서비스가 `snapshot`, 슬롯 키와 캐릭터 고유 ID를 안정적으로 JSON 직렬화한 크기는
최대 2,000,000바이트이며 초과 시 `413`으로 닫힙니다. v377 pure-ASGI 경계는 모든 HTTP
raw body를 2,100,000바이트, `/api/v1/auth` body를 16,384바이트로 제한하고 FastAPI가
JSON을 파싱하기 전에 `413 request_body_too_large`로 닫습니다. 클라이언트가 임의
`userId`를 보내 소유자를 선택할 수 없고, 항상 access token의 현재 계정 ID만 사용합니다.

관리자 회원 API:

- `GET /api/v1/account-admin/bootstrap-status`
- `POST /api/v1/account-admin/bootstrap`
- `GET /api/v1/account-admin/users`
- `GET /api/v1/account-admin/users/{user_id}`
- `POST /api/v1/account-admin/users/{user_id}/status-preview`
- `POST /api/v1/account-admin/users/{user_id}/status-apply`

`bootstrap-status`와 최초 관리자 지정은 로그인 계정만 사용할 수 있습니다. 최초
관리자 지정은 로그인 가능한 관리자가 한 명도 없을 때 현재 로그인 계정과 별도
`X-Admin-Dev-Key`가 모두 확인되어야 한 번만 실행됩니다. 기존 `local-dev`처럼
비밀번호 해시가 없는 과거 placeholder 계정은 로그인 가능한 관리자로 세지 않습니다.

회원 목록·상세·preview는 실제 관리자만 볼 수 있습니다. 상태 apply는 관리자
Bearer 권한에 더해 기존 dev key를 두 번째 방어선으로 유지하고, 정확한 확인 문구,
stale 상태, 본인 정지 금지, 마지막 로그인 가능 관리자 정지 금지를 검사한 뒤
`AdminChangeLog`와 같은 transaction에서 반영합니다. 관리자 API는 비밀번호 해시,
token, 전체 `snapshot_json`을 반환하지 않습니다.

v371은 JWT secret과 공유하지 않는 `OWNER_ADMIN_USERNAME`, `OWNER_ADMIN_EMAIL`,
`OWNER_ADMIN_PASSWORD`를 Git 제외 `.env`에서 잠시 읽는 명시적 one-shot script도
준비합니다. startup에서는 절대 실행하지 않으며 migration head 일치, 관리자 0명,
enable flag, `--apply`, 현재 Git HEAD와 같은 소문자 40자리 `--approved-sha`, project
root·tracked script·tracked index/worktree clean과 환경·SHA·identity fingerprint 확인문을
DB session 생성 전에 요구합니다. 별도 exact-SHA 승인은 계속 필요합니다.
`.env`에 이메일을 적었다는 사실만으로 인증 처리하지 않으며 성공 직후 enable과
password를 제거합니다.

## 서버 기준 저장·브라우저 복구와 캐릭터 전환

- 기존 단일 키 `idleRpgSaveV22`는 삭제하거나 자동 덮어쓰지 않고 명시적 가져오기
  원본으로만 보존합니다.
- 새 로컬 저장 키에는 계정 ID와 캐릭터 고유 ID를 모두 넣습니다.
- DB 저장 키는 캐릭터 고유 ID가 아니라 고정 슬롯 번호 `character-N`을 씁니다.
- 정상 load의 authoritative 원본은 서버 DB snapshot입니다. backend에 snapshot이 있으면
  그 내용을 사용합니다. 서로 다른 local이 남아 있으면 즉시 삭제하지 않고
  `${saveKey}.pre-backend-recovery`에 복구 백업을 만든 뒤 활성 local을 서버본으로
  교체합니다.
- backend snapshot이 비어 있을 때만 계정·캐릭터가 일치하는 local을 복구 원본으로
  사용하고, 게임을 시작한 뒤 같은 직렬 저장 큐에 넣어 서버에 저장합니다. 따라서 평상시
  local이 서버보다 우선한다는 정책이 아닙니다.
- 이전 backend 저장 실패로 해당 계정·캐릭터에 `pending-unsynced` marker가 있고 local도
  존재하면 자동 선택하지 않습니다. `이 기기 저장 사용`은 local을 불러 서버에 다시
  전송하고, `서버 저장 사용`은 local을 복구 백업한 뒤 서버본을 사용하며, 취소는 두
  원본과 marker를 그대로 보존하고 슬롯 화면으로 돌아갑니다.
- 자동 저장, 수동 저장, 캐릭터 전환·로그아웃 최종 저장은 모두 하나의 Promise 직렬 저장
  큐를 사용합니다. 각 요청은 호출 시점 snapshot과 계정·슬롯·캐릭터 ID를 고정해 앞선
  저장이 끝난 뒤 순서대로 실행합니다.
- 캐릭터 선택 뒤에만 게임 load, UI 초기화, 자동 저장 timer가 정확히 한 번 시작됩니다.
- 전환과 로그아웃은 runtime·전투·timer를 먼저 pause하고 기존 저장 큐와 마지막 저장을
  drain합니다. 성공한 뒤에만 선택 상태 또는 token을 정리하고 reload합니다. network/5xx
  실패 시 전환을 중단하고 token·선택 상태를 유지하며 사용자가 게임으로 돌아가 runtime을
  재개하거나 다시 시도할 수 있습니다.
- 저장이나 세션 확인이 `401/403`이면 현재 local과 `pending-unsynced` marker는 보존하고
  access token만 폐기해 로그인 화면으로 돌아갑니다. 재로그인 뒤 marker가 있으면 위
  선택 모달로 복구합니다. network/timeout/`5xx`는 token을 폐기하지 않고 retry 화면이나
  다음 직렬 저장 재시도를 사용합니다.
- `beforeunload`에서는 네트워크 완료를 믿지 않고 현재 캐릭터 로컬 저장만 수행합니다.

## 오류·로그·관리자 응답의 비밀정보 경계

- 인증 경로의 FastAPI `422`는 오류의 `loc`·`type`·`msg`를 유지하되 비밀번호,
  비밀번호 확인과 전체 인증 body의 `input`을 응답에서 제거합니다.
- 인증 실패는 source-controlled stable code를 사용합니다. 요청 제한은 `429
  auth_rate_limited`와 `Retry-After`, 큰 body는 `413 request_body_too_large`를 반환하며,
  모든 `/api/v1/auth` 응답은 `Cache-Control: no-store`입니다.
- Render production의 IP bucket은 edge가 덮어쓴 정확한 `CF-Connecting-IP` 한 값만
  신뢰하고 `X-Forwarded-For`는 사용하지 않습니다. 신뢰 header가 없거나 잘못되면
  rate-limit을 건너뛰지 않고 `503`으로 닫습니다.
- SQLAlchemy engine은 application `DEBUG`와 관계없이 항상 `echo=False`,
  `hide_parameters=True`입니다. 비밀번호 해시와 raw snapshot이 SQL bind parameter나
  오류 로그에 노출되지 않도록 합니다.
- 관리자 save summary는 `saveVersion`, `gold`, `level`, `currentCharacterId`,
  `currentZoneIndex`, `currentZoneType`, 네 item count와 `createdAt`의 명시 allow-list만
  반환합니다. 문자열은 160자로 제한하고 scalar가 아닌 값, 임의 `summary_json` 키와
  전체 `snapshot_json`은 반환하지 않습니다.

## 화면 원칙

- 게임 배경을 어둡게 가린 전체 화면 로그인/회원가입 gate를 먼저 표시합니다.
- 슬롯 화면은 8칸을 항상 보여주며 데스크톱 2열, 좁은 화면 1열입니다.
- 빈 슬롯 생성과 캐릭터 삭제는 브라우저 기본 `alert`/`confirm`을 쓰지
  않고 게임 스타일의 확인·취소 modal로 처리합니다.
- 삭제 전에는 대상 캐릭터, 없어지는 진행 데이터와 확인 문구를 명확히 보여줍니다.
- 사용자 입력과 서버 응답은 `innerHTML`로 직접 삽입하지 않고 text node 또는 escape
  처리를 사용합니다.
- focus 이동, `Escape`, label, 상태 알림, 좁은 화면 버튼 배치를 함께 검증합니다.
- 관리자 페이지는 로그인 및 관리자 권한을 확인하기 전 기존 관리 API와 회원 정보를
  요청하지 않습니다.
- 상단 `접속 캐릭터` 바는 글자·버튼·간격과 터치 영역을 키우고 로그인·캐릭터 선택 뒤
  현재 구역이 `town`일 때만 표시합니다. 필드·보스·빈 보스 구역과 인증/슬롯 gate에서는
  숨깁니다.

## 공개 배포 전 남은 보안 보강

v377 source·migration·Render backend와 Static Site 배포는 완료됐습니다.
공개 회원가입을 확대하기 전 다음 항목을 별도 단계에서
결정하고 검증해야 합니다.

1. 서버측 session/refresh token과 기기별 원격 폐기 또는 현재 access token 정책 확정
2. 다중 기기 동시 접속의 save revision, CAS·낙관적 잠금과 충돌 해결
3. HTTPS 전용 동작, CSP와 XSS 회귀, browser token 저장 방식 재검토
4. 이용약관·개인정보 고지와 계정/데이터 삭제·법적 보존 정책
5. local Brevo 설정·실제 메일·provider 진단 완료; Render 전달 전 key 회전·단일 worker 운영 검증
6. v377 backend image와 legacy static을 같은 승인 단위로 게시·배포하는 exact-SHA gate
7. 소셜 로그인 도입 시 provider-neutral 연결 테이블과 계정 연결/해제 정책

`email-validator 2.3.0`과 Linux dependency lock은 반영됐고 private environment 준비에서
local/production의 `EMAIL_TOKEN_SECRET`·`AUTH_ABUSE_SECRET` 4개를 서로 다르게 생성했습니다.
실제 값은 채팅에 보내지 않으며 local Brevo 전용 API key와 발신자 설정은 완료했습니다.
`8db9bcb` 격리 왕복·local backup과 첫 실패 marker는 stale history로 보존했습니다.
`345872a`의 별도 `recovery1` namespace에서 왕복·fresh backup·local v377 apply를 각각
1회 완료했고 실제 Naver 메일 인증·로그인과 단일 provider 응답 진단도 성공했습니다.
recovery2 왕복·Neon backup·exact apply와 signed backend/static 공개 배포도 각각 1회 완료했습니다.
owner bootstrap은 승인 범위 밖의 별도 단계이고 공개 release는 남은 blocker 완료 뒤 진행합니다.

## 검증 상태

v370 focused/browser/core 최종 검증은 아래와 같이 통과한 과거 baseline입니다.

- backend account auth focused smoke: PASS
- backend account-admin focused smoke: PASS
- frontend account gate와 admin account management smoke: PASS
- v369 아이콘 회귀 smoke: PASS
- Python compileall: PASS
- 관련 JavaScript `node --check`: PASS
- runtime blocking-I/O strict 검사: PASS
- backend route map: 40 operations / PASS
- legacy static build와 static smoke: PASS
- GitHub/GHCR reproducibility hash 5개 동기화와 strict/fail-closed smoke: PASS
- `bash tools/run_smoke_core.sh`: backend `.venv` 활성화, 자식 프로세스
  `DEBUG=false` 조건에서 최종 PASS
- 실제 브라우저 desktop/mobile 로그인·회원가입 화면과 `pending-unsynced` 선택 모달:
  QA PASS, overflow 0, console error 0
- 최종 reviewer가 확인한 즉시 수정 blocker: 없음

v371 backend 이메일 lifecycle·owner one-shot·migration source, v370 backend 회귀,
frontend v371 이메일 계정·v370 character/admin 회귀, Python compileall, JavaScript
`node --check`, runtime blocking-I/O와 48-operation route map smoke는 과거 baseline에서
PASS입니다.
실제 Chrome에서 로그인·회원가입·아이디 찾기·비밀번호 재설정 custom modal을 확인했고,
기본 viewport와 `390×844`에서 mobile `document.scrollWidth=390`, horizontal overflow 0,
console warn/error 0입니다. 이메일 renderer의 외부 asset 0·escape 구조는 smoke로
검증했고 실제 Naver 메일함에서 메일 도착과 링크 동작을 확인했습니다. v377 public-security·semantic-outbox와 기존 v371 이메일
lifecycle focused source 검사 및 전체 core smoke는 PASS입니다. `8db9bcb` 격리 왕복과 local
v295 backup 751 rows는 성공했지만 canonicalization 수정 뒤 SHA-stale입니다. 첫 local apply는
Alembic 전에 안전 중단되어 report 없이 marker만 남았고 기존 namespace는 재사용하지 않습니다.
recovery1 local 적용과 recovery2 격리 왕복·Neon backup·Neon v377 적용을 완료했습니다. 기존 22개
table 데이터 보존과 25개 model table parity가 두 실제 DB에서 PASS했습니다.
local Brevo 설정·발송·인증·로그인은 완료했습니다. `delivery_outcome_unknown` 관찰은 여러
local reload worker의 ownership 단절로 좁혔고 단일 provider 진단은 정상 message ID를
반환했습니다. signed GHCR image와 Render backend/static은 공개 live이며 owner bootstrap은
실행하지 않았습니다.
