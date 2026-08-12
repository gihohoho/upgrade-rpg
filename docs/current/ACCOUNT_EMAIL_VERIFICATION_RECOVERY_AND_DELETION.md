# 이메일 인증·계정 복구·계정 삭제 준비 — v371

```txt
latest: v371.email-verification-recovery-account-deletion-migration-prepared
strict result: email-verification-recovery-account-deletion-migration-prepared
next safe stage: owner-approve-email-validator-install-and-review-v371-migration-source
public Render: backend/static 모두 계속 v351
database migration: source only / not applied
email provider: selected only / account·sender·API key not configured
```

## 결론

v371은 기존 v370의 아이디·비밀번호 계정에 **필수 이메일 인증**, 아이디 찾기,
비밀번호 재설정, 계정 삭제를 더하는 로컬 source 준비 단계입니다. 가입은 아이디와
이메일을 함께 받되, 인증 메일 링크를 완료하기 전에는 access token을 발급하지 않고
게임에 들어갈 수 없게 합니다. 로그인할 때는 아이디 또는 이메일 중 하나를 사용할 수
있습니다.

이 단계에서는 migration 파일과 애플리케이션 코드를 준비할 뿐입니다. 실제 local/Neon
DB write, Alembic `upgrade`·`downgrade`·`stamp`, Brevo 가입·발신자 인증·API key 생성,
실제 메일 발송, `.env` secret 주입, GHCR 게시, Render 환경변수 변경과 backend/static
배포는 모두 **0회**입니다. 공개 Render는 계속 v351입니다.

## 사용자 흐름

```txt
회원가입
  → 아이디 + 이메일 + 비밀번호 입력
  → 인증 메일 발송
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

아이디 찾기·인증 메일 재전송·비밀번호 재설정 요청은 계정이 존재하는지, 실제로
메일을 보냈는지와 관계없이 같은 `202 accepted` 형태를 사용합니다. 공격자가 이메일로
가입 여부를 알아내는 것을 줄이기 위한 경계입니다. 서버는 공급자 timeout이나 모호한
결과를 자동 재시도하지 않으며, 사용자가 다시 요청했을 때만 새 일회용 링크를 만듭니다.

## DB migration 준비

새 Alembic revision `v371_email_identity_lifecycle`은 현재 head
`v295_initial_schema` 다음에 다음 구조를 추가하도록 준비합니다.

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

현재 revision 파일은 **source-only**입니다. migration을 적용하면 Neon schema가 실제로
바뀌고 실행 중인 v351 backend와 schema 계약이 달라지므로 다음 세 작업을 섞지 않습니다.

1. v371 source·dependency·테스트 준비와 commit
2. 정확한 40자리 준비 SHA를 기호가 별도 승인한 뒤 migration preflight와 적용
3. migration 완료 뒤 owner 관리자 bootstrap을 다시 별도 승인

`alembic upgrade head`, `stamp`, 자동 startup migration은 승인 전에 실행하지 않습니다.

## 이메일 유효성 검사 dependency

이메일 주소의 국제화·정규화를 자체 정규식으로 흉내 내지 않고
[`email-validator 2.3.0`](https://pypi.org/project/email-validator/)을 직접 runtime
dependency로 사용하도록 준비했습니다. 패키지가 없으면 약한 검사로 통과시키지 않고
이메일 계정 동작을 `503`으로 닫습니다.

현재 설치·lock 갱신은 기호의 승인을 기다립니다. 승인 뒤에만 backend dependency와
`backend/.venv`에 추가하고 Linux lock 3개와 GHCR 재현성 hash를 함께 갱신합니다. 그전에는
owner bootstrap과 실제 회원가입을 실행하지 않습니다.

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

회원가입 응답에는 access token이 없고 `verification_required` 상태만 있습니다. 로그인
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
원문 token을 반환하지 않습니다.

정적 route map은 전체 48 operations, `GET 21 / POST 26 / DELETE 1`, 중복
method/path 0으로 갱신했고 보고서 smoke가 통과했습니다. auth group은 12개입니다.
자동 보고서는 `docs/generated/BACKEND_ROUTE_MAP.md`에 있습니다.

## 메일 화면과 전달 방식

계정 메일은 외부 image, font, CSS, JavaScript, tracking pixel 없이 source-controlled
HTML과 plain-text 두 버전으로 렌더링합니다. 600px 안쪽의 어두운 남색 패널, 금색
테두리·버튼, 모바일 폭 대응을 사용해 현재 게임 스타일과 맞춥니다. 사용자 아이디는 HTML
escape하고, 제목에 아이디·이메일·token을 넣지 않습니다.

Render Free는 outbound SMTP 포트 `25`, `465`, `587`을 막으므로 이 구성에서는 SMTP가
동작하지 않습니다. [Render Free 공식 제한](https://render.com/docs/free)에 맞춰
Brevo의 고정 HTTPS API `POST https://api.brevo.com/v3/smtp/email`만 사용하도록
준비합니다. Brevo Free는 현재 하루 300건 한도에서 transactional email을 지원하므로
개인 프로젝트의 비용 최소 기준에 맞습니다.
([Brevo Free 요금제](https://help.brevo.com/hc/en-us/articles/208589409-About-Brevo-s-pricing-plans),
[무료 한도](https://help.brevo.com/hc/en-us/articles/208580669-FAQs-What-are-the-limits-of-the-Free-plan),
[전송 API](https://developers.brevo.com/docs/send-a-transactional-email))

실제 Brevo 사용 전에 기호가 직접 해야 하는 작업은 다음 세 가지입니다.

1. Brevo Free 계정 만들기
2. 발신 이메일 주소의 6자리 인증 완료
3. 이 프로젝트 전용 API key 만들기

API key, 발신 이메일과 `EMAIL_TOKEN_SECRET` 값은 채팅·Git·문서·로그에 넣지 않고
Git/Docker 제외 `.env`와 Render secret에만 저장합니다.

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

Brevo 일반 API key는 send-only scope가 아니라
[계정 전체 접근 권한](https://help.brevo.com/hc/en-us/articles/209467485-Create-and-manage-your-API-keys)을
가진 credential입니다. 따라서 이 프로젝트 전용 key를 따로 만들고 짧은 만료일을
선택하며, Render secret에만 저장하고 노출·미사용·integration 종료 시 즉시 삭제합니다.
이 key의 account-wide 위험 때문에 `BREVO_API_KEY` 생성·주입은 migration 승인과 별개의
사용자 확인 단계로 둡니다. 장기적으로 private OAuth app의
`transactional.email:write` 최소 scope가 현재 비용·운영 조건에 맞는지 다시 검토할 수
있지만 v371에서는 사용하지 않습니다.

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

v371이 아래 항목을 모두 끝내는 것은 아닙니다. 공개 회원가입 전에 적어도 다음을
별도 검토·구현·검증합니다.

1. 로그인·가입·인증 재전송·복구·삭제 요청의 IP/이메일별 rate limit과 반복 실패 지연, 만료된 미인증 계정의 안전한 정리·메일 소유자 회수 정책,
   공개 실패 문구·응답 시간 차이로 계정 존재 여부나 인증 상태를 추정하지 못하게 하는 일반화 검토
2. 서버측 session/refresh token, 기기별 원격 폐기 또는 현재 access token 정책 확정
3. ASGI 계층의 JSON 파싱 전 raw request body cap
4. 다중 기기 save revision, 낙관적 잠금과 충돌 해결
5. HTTPS 강제, CSP/XSS 회귀와 browser token 저장 방식
6. 개인정보 처리방침, 데이터 보관·삭제, 문의·복구 절차
7. Brevo sender·anonymous tracking·1개월 retention·preview 미저장 실제 설정 검증
8. backend image와 legacy static을 같은 exact-SHA 단위로 준비·게시·배포하고 rollback 검증

## 승인 단위와 다음 순서

```txt
1. email-validator 2.3.0 설치·lock 갱신 승인
2. v371 source focused/core/browser 검증과 준비 commit
3. exact v371 migration 적용 SHA 별도 승인
4. Brevo 계정·발신자·전용 API key와 Render secret 설정 별도 확인
5. 실제 테스트 메일 1건 별도 확인
6. exact owner bootstrap SHA 별도 승인과 1회 실행
7. owner 이메일 인증·로그인·다중 캐릭터 로컬 통합 확인
8. 공개 보안 gate 완료 뒤 backend/static 동시 release 별도 승인
```

## 현재 검증 결과

- backend v371 이메일 lifecycle focused smoke: PASS
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

Browser URL 정책이 `data:` 이메일 HTML 미리보기를 차단해 우회하지 않았습니다. 따라서
실제 이메일 클라이언트의 시각 QA는 Brevo sender 설정 뒤 테스트 메일 1건 단계로 남깁니다.
전체 `bash tools/run_smoke_core.sh`는 PASS했고 독립 리뷰의 source-prepared 즉시 수정 blocker는 0건입니다. 현재 marker는 source와
migration 파일의 준비를 뜻할 뿐 실제 migration·메일·owner bootstrap·공개 배포 완료를
뜻하지 않습니다.
