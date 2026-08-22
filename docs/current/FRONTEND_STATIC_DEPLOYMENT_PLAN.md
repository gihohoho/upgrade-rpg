# Frontend Static Deployment and v377 Email Auth Release Boundary

## 결론

실제 게임과 관리자 화면은 Vue shell이 아니라 루트 `index.html`, `admin.html`, `src/`입니다. 승인된 v348 준비 SHA로 Render Free Static Site에 이 legacy 화면을 배포했습니다.

현재 공개본은 계속 v351입니다. v370의 로그인·계정별 캐릭터 슬롯 8개 기반, v371의
필수 이메일 가입, 이메일 인증, 아이디 찾기, 비밀번호 재설정, 계정 삭제와 관리자 이메일
상태 UI, v377의 queue·rate-limit·body-limit 대응은 로컬 source에만 있으며 Render Static
Site나 backend에 배포하지 않았습니다. 공개 주소에서 v370~v377 계정 화면이 보이지 않는
것이 정상입니다.

- 서비스 이름: `gihohoho-upgrade-rpg`
- 게임 주소: `https://gihohoho-upgrade-rpg.onrender.com/index.html`
- 관리자 주소: `https://gihohoho-upgrade-rpg.onrender.com/admin.html`
- production API: `https://upgrade-rpg-api.onrender.com/api/v1`
- build command: `node tools/build_legacy_static_site.mjs`
- publish directory: `frontend/legacy-dist`
- auto-deploy: 꺼짐
- custom domain/DNS/payment: 변경 없음

Static Site `srv-d9iu337aqgkc73am4lh0`와 deploy `dep-d9iu33faqgkc73am4m3g`는 exact commit `b13b1775093716800d7361ee1e8f94d8112eefc1`로 Live입니다. v349 recovery SHA 승인 뒤 backend CORS deploy도 정확히 한 번 실행해 exact origin 적용에 성공했습니다.

## 안전한 공개 묶음

`tools/build_legacy_static_site.mjs`는 다음 파일만 `frontend/legacy-dist`에 복사합니다.

- `index.html`
- `admin.html`
- `src/` 아래 `.js`, `.css`
- `src/assets/` 아래 `.png`(현재 AI 특수장비 아이콘 23개 포함)

backend, deploy, docs, tools, Git 정보, `.env`, production secret, `src/**/*.md`는 공개 묶음에 들어가지 않습니다. 출력 폴더는 Git과 Docker build context에서도 제외합니다. 빌드는 symlink, 출력 폴더 밖 참조, 빠진 local asset, token·DB endpoint 형태 문자열을 발견하면 실패합니다.

## 로컬과 공개 API 분리

`src/api/runtime-config.js`가 `game-api-client.js`보다 먼저 실행됩니다.

- `127.0.0.1`, `localhost`, `::1`, `file://`: 기존 local API `http://127.0.0.1:8000/api/v1` 유지
- 그 밖의 HTTPS host: public API `https://upgrade-rpg-api.onrender.com/api/v1` 고정

따라서 현재 로컬 주소는 계속 그대로 쓸 수 있습니다.

- 게임: `http://127.0.0.1:5500/index.html`
- 관리자: `http://127.0.0.1:5500/admin.html`

## CORS와 관리자 경계

backend Render 환경변수 `CORS_ORIGINS`는 `["https://gihohoho-upgrade-rpg.onrender.com"]`으로 저장됐습니다. recovery deploy `dep-d9ivfmvlk1mc73fbcv40`는 40.1초 만에 Live가 됐고 health GET과 OPTIONS preflight는 모두 200이며 exact `Access-Control-Allow-Origin`을 반환합니다.

v350 당시 공개 게임의 CORS 오류는 해결됐지만 `/api/v1/game/master-data` 464,098-byte 응답이 약 1.98초와 1.83초로 frontend의 1.5초 제한을 초과해 기존 JS 데이터로 폴백했습니다. v351에서 timeout을 5초로 늘리고 backend gzip을 적용한 뒤 v355 공개 배포에서 1,346ms·gzip·no-fallback을 확인해 browser master-data 통합을 완료했습니다.

현재 v351 `admin.html` 자체는 공개되지만 frontend에는 `ADMIN_WRITE_DEV_KEY`를 넣지
않습니다. 공개 관리자 화면은 계속 기존 read-only 확인 용도입니다.

v370 로컬 `admin.html`은 계정 로그인을 먼저 확인하고 실제 관리자 Bearer 권한이 있을
때만 기존 관리 API와 회원 목록을 요청합니다. 최초 관리자 bootstrap과 회원 상태 apply의
dev key는 사용자가 직접 입력할 때만 요청 header로 보내며 HTML·JavaScript·저장소에
내장하지 않습니다. 비밀번호 해시, token과 전체 save snapshot은 회원 관리 표에
표시하지 않습니다.

v377 로컬 `index.html`은 signup에 이메일을 필수로 받고 로그인 입력을
`아이디 또는 이메일`로 바꿉니다. 이메일 action URL은 고정된 다음 fragment만
허용합니다.

```txt
/index.html#auth=verify-email&token=...
/index.html#auth=reset-password&token=...
/index.html#auth=delete-account&token=...
```

프런트는 길이·문자·action allow-list를 확인한 fragment token을 읽은 즉시
`history.replaceState`로 주소 표시줄과 history에서 제거하며 `Referrer-Policy:
no-referrer`를 유지합니다. 서버가 정확한 `email_action_token_invalid`를 반환했을 때만
현재 link를 폐기하고, `429`·`413`·network/`5xx`에는 탭 메모리에 보존해 다시 시도합니다.
아이디 찾기·비밀번호 재설정과
계정 삭제의 경고·확인은 browser 기본 alert/confirm이 아니라 게임 스타일의 접근 가능한
모달을 사용합니다. 계정 삭제는 현재 비밀번호, 이메일 링크, 정확한 `계정 삭제` 문구의
세 단계를 UI에서도 빠뜨리지 않습니다.

상단 `접속 캐릭터` 바는 글자, 이름, 버튼, 간격과 터치 영역을 함께 키우고 로그인·캐릭터
선택이 끝난 상태에서 zone type이 `town`일 때만 표시합니다. field, boss,
`boss_empty`, 인증 gate와 슬롯 gate에서는 숨깁니다. desktop/mobile 실제 브라우저
검증에서 기본 viewport의 로그인·회원가입·아이디 찾기·비밀번호 재설정 custom modal과
`390×844`의 `document.scrollWidth=390`, horizontal overflow 0, console warn/error 0을
확인했습니다. v371 이메일 계정, v370 character/admin 회귀 smoke와 관련
`node --check`도 PASS입니다. Browser가 `data:` 이메일 HTML preview를 차단해 우회하지
않았으며 실제 메일 클라이언트 시각 QA는 Brevo sender 설정 뒤 테스트 메일 단계입니다.

v377 응답 문구는 메일 발송 완료를 단정하지 않습니다. 회원가입, 인증 재전송, 아이디
찾기, 비밀번호 재설정과 계정 삭제 메일 요청의 `202`는 queue 접수만 뜻하며 UI는 “요청을
접수했습니다. 도착까지 몇 분 걸릴 수 있습니다”라고 안내합니다. `429`는 응답의
`Retry-After` 초를 표시하고, `413`은 새로고침 뒤 다시 시도하도록 설명합니다. 인증과
session 오류는 stable code allow-list로만 token 폐기 여부를 결정합니다.

v377 static만 먼저 공개하면 이메일·복구 화면이 v351 backend의 없는 API와 schema를
호출하므로 실패합니다. 공개 반영은 v371→v377 migration 완료 뒤 backend image와 legacy
static을 같은 exact-SHA 승인 단위로 준비하고, CORS·인증·캐시·rollback을 함께
검증해야 합니다. auto-deploy와 자동 retry는 계속 끕니다.

`deploy/v377-email-release-guard.example.json`과
`tools/prepare_v377_email_release.py`는 그 미래 release의 fresh GitHub publish lifecycle,
단일 `run_attempt=1`, 새 서명 image digest, 기존 Render service와 필수 환경변수 키 이름만
검증하도록 source에 준비했습니다. focused 회귀는
`tools/smoke/backend/smoke_v377_email_release.py`입니다. 이 도구의 기본 동작은 read-only이고
GitHub·GHCR·Render·Brevo·공개 endpoint를 호출하지 않으므로 현재 v351 공개본이나 provider
상태를 바꾸지 않았으며, 남은 공개 gate를 충족하거나 배포 승인을 대신하지 않습니다.

v370의 정상 load는 서버 DB snapshot이 authoritative입니다. backend snapshot이 있으면
그 내용을 사용하고 서로 다른 local은 `${saveKey}.pre-backend-recovery`에 먼저 백업합니다.
backend가 비어 있을 때만 계정·캐릭터가 일치하는 local을 초기 복구 원본으로 사용해
서버 저장 큐에 넣습니다.

이전 저장 실패의 `pending-unsynced` marker가 있는 경우에는 자동으로 덮어쓰지 않고
게임 UI 모달에서 `이 기기 저장 사용`, `서버 저장 사용`, 취소 중 하나를 선택합니다.
local 선택은 서버 재전송, 서버 선택은 local 백업 후 marker 제거이며 취소 시 두 원본을
그대로 둡니다.

60초 자동 저장, 수동 저장, 캐릭터 전환·로그아웃 최종 저장은 하나의 직렬 Promise 큐를
사용합니다. 전환을 시작하면 runtime·전투·timer를 pause하고 기존 큐와 마지막 저장을
drain합니다. 성공한 뒤에만 선택 상태/token을 지우고 reload하며, network/5xx 실패는
전환을 중단하고 token·선택 상태를 유지해 게임 복귀·runtime 재개 또는 재시도를 제공합니다.

저장·세션 확인의 `401/403`은 local과 `pending-unsynced` marker를 보존한 채 token을
폐기하고 재로그인을 요구합니다. network/timeout/`5xx`는 token을 유지하고 서버 다시
연결 화면이나 다음 저장 retry를 사용합니다. 다중 기기의 서로 다른 최신본을 판정할
서버 revision과 충돌 해결은 아직 없으므로 공개 전 낙관적 잠금 정책을 추가해야 합니다.

## 승인된 v348 실행 결과

1. clean/pushed `main`과 승인 SHA 일치 확인: 성공
2. Render GitHub App을 private `gihohoho/upgrade-rpg` 단일 저장소로 연결: 성공
3. Free Static Site 1개 생성, auto-deploy 비활성화: 성공
4. 승인 exact commit으로 최초 static deploy 1회: Live
5. 실제 `onrender.com` origin 확인: 성공
6. backend `CORS_ORIGINS` 입력과 backend deploy 1회: deploy는 Live, 실제 값은 `[]`로 남아 적용 실패
7. `index.html`, `admin.html`: HTTP 200 및 화면 렌더링 확인
8. browser CORS/read-only API: 실패
9. static raw byte SHA-256: 세 핵심 자산 모두 approved source와 일치
10. 자동 retry·두 번째 deploy: 실행하지 않음

실패 정책에 따라 현재 provider 상태를 보존하고 중단했습니다. 자동 retry, 추가 deploy, DB/Alembic write, admin write, secret 주입, custom domain/DNS, payment 변경은 실행하지 않았습니다.

## v350 recovery 실행 결과

기호가 exact SHA `e64d42d812d78de023dc6cbd7f960263bc1c2d15`를 승인했습니다. CORS 행의 현재 `[]`를 먼저 표시하고, Edit에서 exact origin으로 전체 교체한 뒤 포커스를 이동해 폼 값과 14개 unique key를 재확인했습니다. `Save and deploy`는 정확히 한 번 실행했고 추가 retry는 없었습니다.

배포 뒤 actual value와 preflight를 재확인해 recovery 성공을 확정했습니다. 공개 관리자 새 탭에서는 이전 `RpgAdminFieldHelp is not loaded` 로그가 재현되지 않았습니다. frontend 재배포는 실행하지 않았습니다.

추가 Render 환경변수 변경이나 provider deploy가 필요해지면 새 준비 commit의 정확한 40자리 SHA를 기호가 승인한 뒤에만 실행합니다.

## 콘텐츠 작업 시작 기준 — v355 충족

v350 당시에는 콘텐츠 추가·수정을 시작하기 좋은 시점이 아니었습니다. 아래 두 조건은 v355에서 모두 충족됐고 v356에서 첫 장비 공식 변경을 시작했습니다.

1. 공개 게임이 backend master-data를 timeout·폴백 없이 로드: 완료
2. 관리자 guarded 콘텐츠 작업 흐름이 안전하게 검증됨: 완료

## 필요할 수 있는 사용자 조치

`email-validator 2.3.0` 설치·Linux lock, v377 public-security source와 private environment
준비는 완료됐습니다. `8db9bcb` 격리 왕복·local backup은 새 canonicalization SHA에 stale이고
첫 local apply는 Alembic 전에 안전 중단됐습니다. 기존 marker는 보존하고 `345872a`의 별도
`recovery1` 왕복·fresh backup·local v377 apply를 각각 1회 완료했습니다. 다음 순서는 Brevo
계정·발신자·전용 API key를 local에 구성하고 실제 테스트 메일을 확인하는 것입니다. 비밀번호, API key,
dev key와 token은 채팅에 보내지 않으며 owner bootstrap은 이메일 rollout과 별도입니다.

서버측 session/refresh·기기별 폐기, 다중 기기 save revision/CAS, HTTPS/CSP/XSS와 browser
token 저장 방식, 개인정보·삭제·법적 보존 정책, provider 실제 설정·테스트와 별도
exact-SHA deploy gate 전에는 v377을 공개 배포하지 않습니다. 준비된 source-only release
guard도 이 순서를 우회하지 않습니다.
