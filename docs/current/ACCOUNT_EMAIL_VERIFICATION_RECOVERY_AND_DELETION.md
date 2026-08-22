# 이메일 인증·계정 복구·계정 삭제 준비 — v377

```txt
latest: v377.public-email-rollout-deployed
strict result: public-email-rollout-deployed
next safe stage: monitor-v377-public-email-delivery-and-remaining-account-gates
public Render: backend/static v377 Live
database migration: local/Neon v377 / apply 1회씩 / stamp·downgrade 0회
email provider: local Brevo real Naver delivery verified / Render configured
email rollout approval/execution: yes/public-live
```

## v376 실행 승인

기호는 실질적인 이메일 인증 rollout에 필요한 공개 보안 구현, 필요한 unapplied migration source, isolated PostgreSQL 왕복, gate 통과 뒤 local/Neon migration, Brevo/Render secret 설정, 테스트 메일, backend/static 배포와 실제 이메일 end-to-end 확인을 승인했습니다. 정상 경로의 같은 범위를 단계마다 다시 묻지 않지만, 소비된 one-attempt marker 뒤 새 recovery는 새 namespace와 exact 범위를 별도로 승인받습니다. Brevo 가입·발신자 소유 확인·API key 입력처럼 Codex가 대신할 수 없는 행동은 DB 단계 뒤 한 번에 요청합니다. owner bootstrap, DB reset·seed·restore와 이메일 인증에 무관한 기능 변경은 포함되지 않습니다.

## 결론

v371은 새 아이디·비밀번호 계정에 **필수 이메일 인증**, 아이디 찾기,
비밀번호 재설정과 계정 삭제 lifecycle을 더했습니다. 이메일 열이 없는 v295 기존 계정은
기존 아이디·비밀번호 접근을 유지하고 `emailVerified=false`로 표시합니다. v377은 이 흐름을 공개하기 전에
필요한 PostgreSQL HMAC rate bucket, JSON 파싱 전 body cap, stable auth error와 durable
semantic outbox를 source로 준비합니다. 가입은 아이디와 이메일을 함께 받되, 인증 메일
링크를 완료하기 전에는 access token을 발급하지 않고 게임에 들어갈 수 없게 합니다.
로그인할 때는 아이디 또는 이메일 중 하나를 사용할 수 있습니다.

private environment 준비는 security artifact 535개의 ACL을 비공개로 고정하고 local/production에
서로 다른 email/abuse secret 4개를 값 출력 없이 생성해 완료했습니다. `8db9bcb`의 synthetic
isolated 왕복과 local v295 custom backup 751 rows도 각각 1회 성공했지만 canonicalization 수정
뒤에는 SHA-stale입니다. 이후 recovery1에서 local을, recovery2에서 Neon을 fresh backup과
함께 v377로 각각 1회 upgrade했습니다. stamp·downgrade는 0회입니다.
Brevo 프로젝트 전용 API key·검증된 sender와 privacy 설정을 local 범위에서 준비하고 실제
Naver 메일 수신→링크 인증→로그인→캐릭터 슬롯 8개 진입까지 확인했습니다. 첫 발송은 local
호출 IP 미허용으로 401 terminal 실패했고 자동 재시도하지 않았습니다. IP 허용 뒤 새 요청은
실제 전달됐지만 여러 local reload worker가 겹친 환경에서 provider 수락 뒤 worker ownership이
끊겨 `delivery_outcome_unknown` terminal이 됐습니다. 단일 직접 provider 진단은 2초 이내
message ID를 정상 반환했습니다. GHCR signed image와 Render 환경변수·backend/static을
단일 시도로 배포했고 공개 Render는 v377 live입니다.

## 사용자 흐름

```txt
회원가입
  → 아이디 + 이메일 + 비밀번호 입력
  → 가입과 인증 메일 요청을 durable queue에 함께 기록
  → worker가 인증 메일 1회 전달 시도
  → 이메일 링크 확인
  → 로그인
  → 캐릭터 슬롯 8개
  → 캐릭터 선택·생성
  → 게임 시작

아이디 찾기
  → 이메일 입력
  → 존재 여부를 드러내지 않는 동일 응답
  → 인증된 계정이면 아이디 안내 메일 발송

비밀번호 재설정
  → 이메일 입력
  → 존재 여부를 드러내지 않는 동일 응답
  → 일회용 링크에서 새 비밀번호 설정
  → 기존 access token 전체 무효화

계정 삭제
  → 로그인 상태에서 삭제 범위 미리보기
  → 현재 비밀번호 재확인
  → 이메일 링크 확인
  → 게임 UI에서 `계정 삭제` 문구 입력
  → 일반 회원 계정과 종속 데이터 영구 삭제
```

회원가입·아이디 찾기·인증 메일 재전송·비밀번호 재설정·계정 삭제 메일 요청은 처리나
전송 완료가 아니라 queue 접수를 뜻하는 `202 accepted` 문구를 사용합니다. discovery
경로는 계정 존재와 실제 queue 상태를 공개 응답으로 구분하지 않고 최소 응답 시간과
jitter를 적용합니다. 서버는 공급자 timeout이나 결과 불명 호출을 자동 재시도하지
않으며, 사용자가 다시 요청한 경우에만 별도 semantic job을 접수합니다.

## DB migration 준비

Alembic source는 `v295_initial_schema` → `v371_email_identity_lifecycle` →
`v377_auth_email_public_security` 순서입니다. local/Neon DB는 모두 v377입니다.
v371 revision은 다음 identity 구조를 추가하도록 준비합니다.

`users` 추가 열:

- `email_original`: 화면과 메일에 사용할 원래 표기, 기존 계정을 위해 nullable
- `email_canonical`: 비교·로그인·고유성 확인용 정규화 주소, unique index, 기존 계정을
  위해 nullable
- `email_verified_at`: 메일 링크 인증 완료 시각
- `auth_version`: 비밀번호 재설정 등 전체 access token 폐기에 사용하는 정수

새 `user_email_action_tokens` 테이블:

- 목적은 `verify_email`, `password_reset`, `account_deletion` 세 종류만 허용
- 브라우저와 이메일에는 32바이트 이상 CSPRNG 원문 token을 전달
- DB에는 별도 `EMAIL_TOKEN_SECRET`으로 만든 HMAC-SHA256 digest만 보관
- 만료 시각, 사용 완료 시각, 전달 시도·성공·실패 상태와 제한된 공급자 message ID만
  보관
- 기본 만료: 이메일 인증 24시간, 비밀번호 재설정 30분, 계정 삭제 확인 30분
- token 원문, 비밀번호 원문·해시, 이메일 본문은 DB 행과 로그에 저장하지 않음
- 사용자 삭제 시 token 행도 `ON DELETE CASCADE`로 삭제

기존 v351/v370 계정의 이메일은 임의 주소로 채우거나 자동 인증하지 않습니다. 기존 행의
두 이메일 열은 `NULL`로 남겨 별도 owner 정책과 migration 실행 뒤 안전하게 보완합니다.
새 회원가입만 유효한 이메일을 필수로 요구합니다.

v377 revision은 다음 두 테이블을 추가하도록 준비합니다.

- `auth_rate_limit_buckets`: 정책 scope와 `AUTH_ABUSE_SECRET` HMAC subject digest,
  window/request/failure/cooldown 시각만 저장하며 원문 IP·이메일·아이디·action token은
  저장하지 않음
- `auth_email_outbox`: purpose, HMAC target digest, pending/preparing/sending과 terminal
  상태, 최대 1회의 provider attempt와 제한된 message ID/error code만 저장하며 수신자,
  원문 token, 제목·본문은 저장하지 않음

두 revision은 local/Neon DB에 적용했습니다. `8db9bcb`의 synthetic 왕복과
local backup, 첫 실패 marker는 역사 증거로 보존합니다. `345872a`의 별도 recovery1
namespace에서 새 왕복·backup·local apply를 각각 1회 완료했고 기존 22개 table 데이터
변화 0과 25개 model table parity를 확인했습니다.

recovery2 isolated 왕복·Neon backup·apply는 각각 1회 완료했습니다. 다음 단계는 공개 테스트
메일 delivery와 outbox terminal 상태를 값 노출 없이 관찰하는 것입니다. 동일 메일 자동 재시도나
기존 action 재실행은 하지 않습니다.

일반 `alembic upgrade head`, `stamp`, 자동 startup migration은 사용하지 않습니다. 실제
target apply는 lock/statement timeout, exact source·target·action·backup 확인을 모두 갖춘
v377 guard만 사용하며 production DB downgrade·restore를 실행하지 않습니다. owner
bootstrap은 이 rollout 승인에 포함되지 않은 별도 단계입니다.

## 이메일 유효성 검사 dependency

이메일 주소의 국제화·정규화를 자체 정규식으로 흉내 내지 않고
[`email-validator 2.3.0`](https://pypi.org/project/email-validator/)을 직접 runtime
dependency로 사용하도록 준비했습니다. 패키지가 없으면 약한 검사로 통과시키지 않고
이메일 계정 동작을 `503`으로 닫습니다.

기호의 승인으로 `email-validator==2.3.0`과 전이 dependency `dnspython==2.8.0`을
`backend/.venv`, Linux lock 3개와 GHCR 재현성 hash에 반영했습니다. package를 임의로
제거하면 이메일 동작은 계속 `503`으로 fail-closed합니다. local migration은 완료됐지만
local Brevo 실제 회원가입·인증·로그인은 완료했고 owner bootstrap은 별도 승인 전입니다.

## API source 계약 — route map 확정

현재 source가 준비하는 공개 경로:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/verify-email`
- `POST /api/v1/auth/resend-verification`
- `POST /api/v1/auth/recover-username`
- `POST /api/v1/auth/request-password-reset`
- `POST /api/v1/auth/reset-password`
- `POST /api/v1/auth/account-deletion/confirm`

Bearer 로그인이 필요한 경로:

- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/account-deletion/preview`
- `POST /api/v1/auth/account-deletion/request`

회원가입도 queue 접수를 뜻하는 HTTP `202`이며 응답에는 access token이 없고
`verification_required` 상태만 있습니다. 로그인
token은 DB의 현재 `authVersion`을 함께 확인합니다. 이메일 인증과 비밀번호 재설정은
계정의 `authVersion`을 증가시키고 남은 이메일 작업 token을 모두 소진 처리합니다.

링크는 서버가 설정한 고정 `PUBLIC_FRONTEND_ORIGIN`에만 만듭니다. 요청의 `Host`,
`returnUrl`이나 사용자가 보낸 redirect URL은 신뢰하지 않습니다.

```txt
/index.html#auth=verify-email&token=...
/index.html#auth=reset-password&token=...
/index.html#auth=delete-account&token=...
```

민감 token은 query string이 아니라 URL fragment에 놓고, 프런트는 읽은 직후
`history.replaceState`로 주소 표시줄과 history에서 제거하도록 준비합니다.
`index.html`은 `Referrer-Policy: no-referrer`를 사용합니다. API 응답·로그·관리자 화면은
원문 token을 반환하지 않습니다. 프런트는 길이·문자·action allow-list가 맞지 않는
fragment를 즉시 버리고, 정상 link는 `email_action_token_invalid`일 때만 폐기합니다.
`429`, `413`, network/`5xx`에서는 현재 탭 메모리의 link를 보존해 안전하게 다시 시도합니다.

v377은 모든 이메일 인증 POST에 두 단계 request protection을 적용합니다. pure-ASGI
middleware가 body parsing 전에 IP bucket을 소비하고, Pydantic 검증 뒤 route가 normalized
email·identifier·token·user subject bucket을 확인합니다. PostgreSQL에는 원문 subject가
아니라 별도 `AUTH_ABUSE_SECRET` HMAC digest만 저장합니다. 반복 실패는 제한된 cooldown과
응답 지연을 사용합니다.

- `/api/v1/auth` raw body: 16,384바이트
- 그 밖의 전체 HTTP raw body: 2,100,000바이트
- 요청 제한: `429 auth_rate_limited`, `Retry-After` header와 같은 초 수의 response meta
- 큰 body: JSON 파싱 전 `413 request_body_too_large`
- 모든 auth 응답: `Cache-Control: no-store`
- Render client IP: edge가 덮어쓴 정확한 `CF-Connecting-IP`만 신뢰, `X-Forwarded-For`는
  사용하지 않음; header 누락·잘못된 IP는 `503 auth_protection_unavailable`

정적 route map은 전체 48 operations, `GET 21 / POST 26 / DELETE 1`, 중복
method/path 0으로 갱신했고 보고서 smoke가 통과했습니다. auth group은 12개입니다.
자동 보고서는 `docs/generated/BACKEND_ROUTE_MAP.md`에 있습니다.

## 메일 화면과 전달 방식

계정 메일은 외부 image, font, CSS, JavaScript, tracking pixel 없이 source-controlled
HTML과 plain-text 두 버전으로 렌더링합니다. 600px 안쪽의 어두운 남색 패널, 금색
테두리·버튼, 모바일 폭 대응을 사용해 현재 게임 스타일과 맞춥니다. 사용자 아이디는 HTML
escape하고, 제목에 아이디·이메일·token을 넣지 않습니다.

API transaction은 메일을 직접 보내지 않고 semantic job만 durable outbox에 commit합니다.
실제 계정이 없는 discovery 요청도 같은 형태의 decoy job을 기록할 수 있어 공개 응답과 DB
처리 경로의 차이를 줄입니다. outbox에는 수신자 주소, 원문 action token, 렌더링한 제목·본문을
보관하지 않습니다. worker가 `FOR UPDATE SKIP LOCKED`로 job을 claim한 뒤 현재 계정 이메일을
다시 확인하고, 필요한 경우에만 새 token과 본문을 메모리에서 만듭니다.

공급자 호출 직전에 `sending`, `attempt_count=1`을 commit하므로 호출을 시도한 job은 자동
재시도하지 않습니다. 호출 전 멈춘 `preparing`만 다시 queue에 넣을 수 있고 오래된
`sending`은 결과 불명 실패로 종료합니다. 인증 재전송·비밀번호 재설정·삭제 요청의 기존
유효 link는 새 메일이 성공으로 확정되기 전에는 소진하지 않습니다. 새 전달 성공 뒤에만
같은 계정·목적의 이전 token을 폐기하므로 공급자 실패가 기존 정상 link를 깨뜨리지 않습니다.

Render Free는 outbound SMTP 포트 `25`, `465`, `587`을 막으므로 이 구성에서는 SMTP가
동작하지 않습니다. [Render Free 공식 제한](https://render.com/docs/free)에 맞춰
Brevo의 고정 HTTPS API `POST https://api.brevo.com/v3/smtp/email`만 사용하도록
준비합니다. Brevo Free는 현재 하루 300건 한도에서 transactional email을 지원하므로
개인 프로젝트의 비용 최소 기준에 맞습니다.
([Brevo Free 요금제](https://help.brevo.com/hc/en-us/articles/208589409-About-Brevo-s-pricing-plans),
[무료 한도](https://help.brevo.com/hc/en-us/articles/208580669-FAQs-What-are-the-limits-of-the-Free-plan),
[전송 API](https://developers.brevo.com/docs/send-a-transactional-email))

local 실제 Brevo 검증을 위해 기호가 직접 해야 했던 다음 세 가지는 완료됐습니다.

1. Brevo Free 계정 만들기
2. 발신 이메일 주소의 6자리 인증 완료
3. 이 프로젝트 전용 API key 만들기

API key, 발신 이메일과 `EMAIL_TOKEN_SECRET` 값은 채팅·Git·문서·로그에 넣지 않고
Git/Docker 제외 `.env`와 Render secret에만 저장합니다.

local 프로젝트 key는 1개월 만료로 만들고 ignored `backend/.env`에만 저장했습니다. Render
secret에는 아직 전달하지 않았으며, 실제 sender 주소·key·수신자·action token은 문서와
Git evidence에 기록하지 않습니다.

## Brevo 개인정보·credential gate

Brevo는 기본적으로 수신자별 open/click을 추적합니다. 실제 메일을 보내기 전에
[transactional anonymous tracking](https://help.brevo.com/hc/en-us/articles/11643306229906-Can-I-anonymize-the-tracking-of-opens-and-clicks-for-my-emails)을
켜 수신자 이메일·IP와 개별 open/click 연결을 익명화합니다. 이 옵션도 전체 open/click
집계 자체를 없애지는 않는다는 점을 개인정보 고지에 반영합니다.

Transactional log와 전송한 HTML preview는 기본값으로 무기한 보존될 수 있으므로
[retention rule](https://help.brevo.com/hc/en-us/articles/4415743225746-Configure-a-custom-retention-period-for-your-transactional-logs-and-email-previews)을
다음과 같이 설정합니다.

- log retention: 공급자가 허용하는 최단 기간인 1개월
- email preview: 새 메일에 대해 `Never store previews`
- 별도 CSV export나 장기 local 보관: 하지 않음

위 anonymous tracking·1개월 log retention·`Never store previews`는 실제 Brevo 계정에서
확인·저장했습니다. local 호출 IP만 API key 허용 목록에 추가했으며 그 주소도 문서나
artifact에 남기지 않습니다.

Brevo 일반 API key는 send-only scope가 아니라
[계정 전체 접근 권한](https://help.brevo.com/hc/en-us/articles/209467485-Create-and-manage-your-API-keys)을
가진 credential입니다. 따라서 이 프로젝트 전용 key를 따로 만들고 짧은 만료일을
선택하며, Render secret에만 저장하고 노출·미사용·integration 종료 시 즉시 삭제합니다.
이 key의 account-wide 위험 때문에 `BREVO_API_KEY` 생성·주입은 DB migration과 분리한
사용자 행동 단계로 둡니다. 장기적으로 private OAuth app의
`transactional.email:write` 최소 scope가 현재 비용·운영 조건에 맞는지 다시 검토할 수
있지만 v377에서는 사용하지 않습니다.

## 만료된 미인증 identity 회수

가입만 하고 인증하지 않은 계정은 background bulk delete하지 않습니다. 같은 아이디나
이메일로 새 가입 요청이 들어왔을 때 생성 후 168시간이 지난 충돌 계정을 row lock으로
확인하고, 다음 조건을 모두 만족할 때만 그 요청 안에서 identity를 회수합니다.

- 활성·비관리자·password-backed 계정이고 이메일이 아직 미인증
- 관리자 role·감사 기록이 없음
- save snapshot, item, inventory/equipment slot, character skill, mailbox 데이터가 없음

하나라도 만족하지 않으면 기존 identity를 보존하고 conflict로 닫습니다. 이 정책은
실제 사용 가능한 계정이나 진행 데이터를 정리 작업이 추측해 삭제하지 않도록 하는
on-demand 최소 회수 경계입니다.

## 계정 삭제 안전 경계

삭제 전 미리보기는 캐릭터 수, 서버 snapshot 수, 삭제되는 데이터 종류와 마스킹 이메일만
보여 줍니다. raw snapshot은 반환하지 않습니다. 현재 비밀번호가 맞아야 이메일 링크를
요청할 수 있고, 링크를 연 뒤 게임 모달에서 `계정 삭제`를 정확히 입력해야 합니다.

삭제는 일반 회원의 `users` 행을 hard delete하고 기존 FK cascade 범위의 profile,
캐릭터 snapshot, 인벤토리·장비·스킬·우편 데이터와 이메일 작업 token을 함께 지우도록
준비합니다. 복구할 수 없다는 문구를 실행 전에 보여 줍니다. 관리자 계정, 관리자 감사
기록에 연결된 계정, 마지막 관리자 위험은 삭제 경로에서 fail-closed로 막습니다.
브라우저 local cache는 서버 삭제 성공 뒤 해당 계정 범위만 정리합니다.

개인정보 처리방침, 보관 기간, 이용자 요청 처리, 법적 보존 예외는 아직 확정하지 않았으므로
공개 회원가입 전 별도 문서와 사용자 확인이 필요합니다.

## 관리자 회원 화면

회원 목록에는 마스킹 이메일과 인증 완료/대기 상태만 표시하고, 권한을 확인한 상세
화면에서만 전체 이메일을 보여 주도록 준비합니다. 이메일 주소로 검색할 수 있지만
비밀번호 원문·해시, access token, 이메일 작업 token, 공급자 API key·message body와
전체 save snapshot은 관리자 응답과 화면에 노출하지 않습니다.

## 접속 캐릭터 표시

상단 `접속 캐릭터` 바는 글자, 캐릭터명, 버튼, 내부 간격과 터치 영역을 함께 키웁니다.
로그인과 캐릭터 선택이 끝났고 현재 구역이 `town`일 때만 보이며, 필드·보스·빈 보스
구역과 인증/슬롯 gate에서는 숨깁니다. 화면 폭이 좁아도 버튼과 텍스트가 겹치지 않도록
반응형 배치를 함께 검증합니다.

## 최상위 owner 관리자 `.env` 준비

관리자 비밀번호를 `JWT_SECRET_KEY`와 공유하지 않습니다. 다음 별도 값을 Git에서 제외된
`backend/.env`에 잠시 넣는 1회 script만 준비합니다.

```txt
OWNER_ADMIN_BOOTSTRAP_ENABLED=false
OWNER_ADMIN_USERNAME=
OWNER_ADMIN_EMAIL=
OWNER_ADMIN_PASSWORD=
```

FastAPI 시작·reload·migration 때 자동 실행하지 않습니다. script 기본 모드는 read-only
inspect이고, 실제 적용은 다음 조건을 모두 요구합니다.

- `OWNER_ADMIN_BOOTSTRAP_ENABLED=true`
- DB revision이 로컬 Alembic head와 정확히 일치
- 로그인 가능한 기존 관리자가 0명
- `--apply`와 소문자 40자리 `--approved-sha`; 승인 SHA가 현재 Git HEAD와 정확히 일치
- project root 일치, 실행 script tracked, tracked Git index/worktree clean
- 환경·승인 SHA·아이디/이메일 SHA-256 identity fingerprint를 묶은 정확한 확인 문구
- 아이디·이메일·16자 이상 문자/숫자/기호 비밀번호 검증
- 한 transaction에서 create 또는 기존 동일 계정 promote와 감사 로그 기록

승인 SHA·Git 상태·확인 문구 검사는 DB engine/session factory를 만들기 전에 fail-closed로
끝납니다. 종료 코드는 ready/apply 성공 `0`, 정상적인 안전 차단 `3`, 예상 밖 오류·CLI
사용법 오류 `2`로 구분합니다. 확인 문구에는 아이디·이메일 원문 대신 안정적인 identity
fingerprint만 들어가며 비밀번호는 명령행·출력에 넣지 않습니다.

`.env`에 주소를 적었다는 사실은 이메일 소유 증명이 아니므로 owner 계정도 자동 인증하지
않습니다. 적용 뒤 정상 인증 메일 링크를 완료해야 로그인할 수 있습니다. 성공 즉시
`OWNER_ADMIN_BOOTSTRAP_ENABLED=false`로 돌리고 `OWNER_ADMIN_PASSWORD`를 `.env`에서
비우거나 제거합니다. 비밀번호와 hash는 출력하지 않습니다.

실제 owner bootstrap은 migration 적용과 이메일 공급자 설정이 끝난 뒤, 새로운 정확한
준비 SHA를 기호가 별도 승인한 경우에만 1회 실행합니다.

## 아직 남은 공개 보안 gate

v377 source가 아래 항목을 모두 끝내는 것은 아닙니다. 공개 회원가입 전에 적어도 다음을
별도 검토·구현·검증합니다.

1. 서버측 session/refresh token, 기기별 원격 폐기 또는 현재 access token 정책 확정
2. 다중 기기 save revision, CAS·낙관적 잠금과 충돌 해결
3. HTTPS 강제, CSP/XSS 회귀와 browser token 저장 방식
4. 개인정보 처리방침, 데이터 보관·삭제, 문의·복구와 법적 보존 절차
5. local Brevo 실제 설정·메일·provider 진단 완료; Render 전달 전 key 회전·단일 worker 운영 검증
6. backend image와 legacy static을 같은 exact-SHA 단위로 준비·게시·배포하고 rollback 검증

## 승인 단위와 다음 순서

```txt
1. old `8db9bcb` evidence와 완료된 recovery1 marker·report 보존
2. 완료: Brevo 계정·발신자·privacy 설정·전용 API key와 local 설정
3. 완료: 실제 Naver 메일과 가입·인증·로그인·캐릭터 슬롯 진입
4. 완료: local multi-worker ownership 단절과 단일 provider 정상 응답 진단
5. 완료: final source의 recovery2 왕복·Neon backup·exact apply
6. 완료: exact v377 backend/static 준비·게시·배포와 공개 422/202/health 확인
7. 현재: 공개 delivery와 outbox terminal 상태 관찰
8. server session/revoke, save CAS, CSP/XSS/browser token, 개인정보 gate 완료
```

v376에서 승인된 이메일 rollout의 정상 범위와 이번 local recovery 요청은 이어집니다. Brevo
가입·발신자 소유 확인·privacy 설정·API key 입력은 완료했습니다. owner bootstrap은 이 목록과
별도입니다.

## 현재 검증 결과

v377 source에서 현재 완료가 확인된 focused 결과:

- backend v377 public auth security focused smoke: PASS
- backend v377 semantic email outbox focused smoke: PASS
- backend v371 이메일 lifecycle focused smoke: PASS

아래는 v371 source-prepared checkpoint에서 완료한 과거 baseline입니다.

- backend owner 관리자 one-shot fail-closed smoke: PASS
- v371 migration source parity smoke: PASS
- backend v370 account/auth와 account-admin 회귀 smoke: PASS
- backend route map: 48 operations, `GET 21 / POST 26 / DELETE 1`, duplicate 0 / PASS
- Python compileall: PASS
- runtime blocking-I/O strict: PASS
- frontend v371 이메일 계정 focused smoke: PASS
- frontend v370 character gate와 admin account 회귀 smoke: PASS
- 관련 JavaScript `node --check`: PASS
- 실제 Chrome 기본 viewport: 로그인·회원가입·아이디 찾기·비밀번호 재설정 custom modal
  표시와 상호작용 확인, console warn/error 0
- 실제 Chrome `390×844`: `document.scrollWidth=390`, horizontal overflow 0,
  console warn/error 0
- 이메일 renderer: 외부 asset 0, HTML escape와 plain-text fallback 구조 smoke PASS

Browser URL 정책이 `data:` 이메일 HTML 미리보기를 차단해 우회하지 않았습니다. 실제 Naver
메일함에서 제목·발신자·인증 링크 도착과 링크 동작을 확인했습니다.
기존 v371 browser 결과는 과거 baseline의 PASS이며 v377 전체
`bash tools/run_smoke_core.sh`도 backend `.venv`·`DEBUG=false` 조건에서 PASS했습니다.
`8db9bcb` migration evidence는 stale history로 보존했고 `345872a` recovery1 왕복·backup·local
apply는 성공했습니다. local/Neon DB는 v377이고 인증 보호 503은 사라졌습니다.
signed backend image와 static은 공개 live이며 owner bootstrap은 실행하지 않았습니다. local 실제 메일은
완료했고 다음은 공개 delivery와 provider/outbox 상태 관찰입니다.
