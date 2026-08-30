# Upgrade RPG Codex working rules — v377

이 파일은 저장소 전체에 적용되는 **장기 규칙**입니다. 새 작업은 다음 순서로 시작합니다.

1. [AGENTS.md](AGENTS.md)
2. [NEXT_CHAT_HANDOFF.md](NEXT_CHAT_HANDOFF.md)
3. [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)
4. 작업과 직접 관련된 `docs/current/`, `docs/reference/`, `docs/contracts/` 문서

과거 구현 세부는 처음부터 읽지 않고 필요할 때만 `docs/archive/history/`에서 검색합니다.

## 사용자와 작업 방식

- 사용자는 코딩을 잘 모르는 **기호**입니다. 항상 쉽고 구체적인 한국어로 설명하고 기록합니다.
- `.env`와 같은 환경변수와 로컬파일사용 및 브라우저탐색 등 전체 권한을 승인합니다.
- 사용자가 직접 실행해야하는 명령에 한해서 바로 위에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적습니다.
- backend 가상환경은 `backend/.venv`입니다. Git Bash에서는 `backend`에서 `source .venv/Scripts/activate`로 켭니다.
- Vue/npm은 `frontend/vue-app`에서 실행하며 Python `.venv`가 필요 없습니다.
- 필요한 extension, 권한, 설치, 외부 계정 작업이 있으면 기호에게 요청하고 해결될 때까지 handoff에 남깁니다.
- Codex는 정상 실행 중인 backend `127.0.0.1:8000`, Vue `127.0.0.1:5173`, legacy static `127.0.0.1:5500` 서버를 재사용합니다.
- legacy 브라우저 검증은 `http://127.0.0.1:5500/index.html`과 `/admin.html`을 사용합니다. `file://`는 사용하지 않습니다.
- Windows 전역 `DEBUG=release`는 backend 설정과 충돌하므로 backend 검사 자식 프로세스에서만 `DEBUG=false`로 덮어씁니다.
- 변경·검증 뒤 Codex가 직접 `git status`, 선택적 stage, commit, push를 수행합니다. 사용자 변경은 stage하지 않습니다.
- 서버를 재시작하지 않았으면 완료 답변에 `서버 재시작 불필요`라고 적습니다.
- 모든 작업의 마지막에는 [AGENTS.md](AGENTS.md), [NEXT_CHAT_HANDOFF.md](NEXT_CHAT_HANDOFF.md), [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)를 현재 상태와 맞추고, 변경 주제와 관련된 Markdown을 선택적으로 검색해 통합·이동·archive·삭제 필요 여부까지 점검합니다. 관련없는 Markdown문서를 전부 점검하지 않고, 의미 없는 복사본이나 단계별 새 문서를 만들지 않습니다.
- Obsidian의 ignored 로컬 vault 설정, 북마크, 검색, Graph 색상 그룹과 workspace는 사용자가 직접 관리하지 않고 Codex가 탐색 효율 중심으로 유지합니다. Graph가 복잡해져도 문서 범위를 숨기기보다 폴더별로 구분하며, 프로젝트 동작은 Obsidian에 의존하지 않습니다.

## 실행 효율과 자체 피드백

- 실행 효율과 자체 피드백의 목적은 CODEX의 작업속도 최적화와 작업 효율성 극대화 입니다.
- 작업 시작 시 변경 범위, 필요한 실행 환경, 검증 목록을 한 번 정하고 같은 확인을 습관적으로 반복하지 않습니다. 간단한 문서 작업에는 sub-agent, 브라우저, 서버 상태 확인, 전체 core smoke를 사용하지 않습니다.
- PowerShell에서 `bash`만 호출하면 WSL로 잘못 연결될 수 있습니다. 전체 core smoke는 항상 설치된 Git Bash를 명시하고 같은 명령 안에서 `source backend/.venv/Scripts/activate`, `DEBUG=false`, `bash tools/run_smoke_core.sh` 순서로 실행합니다.
- 문서만 바꾼 작업은 문서 구조·handoff·strict readiness만 한 번 검사합니다. 포맷만 바꾼 CSS는 AST 의미 동등성과 관련 focused smoke만 검사합니다. 동작 코드의 전체 core는 통합이 끝난 뒤 한 번만 실행하며, 이후 결과 문구만 고친 경우 다시 실행하지 않습니다.
- 성공한 명령의 exit code와 출력은 그대로 신뢰합니다. 성공한 `git push` 뒤 원격 추적 상태를 다시 확인하거나, 이미 적용·재실행 검증한 Obsidian을 단순 확인 목적으로 다시 열지 않습니다.
- 환경 지정 실수나 불필요한 반복이 생기면 작업 종료 전에 원인을 짧게 자체 점검하고 다음 실행 규칙에 반영합니다. 자체 점검을 증명하기 위한 추가 명령이나 보고서는 만들지 않습니다.

## 변경 품질

- 새 추상화·의존성·파일보다 기존 코드와 표준 기능을 먼저 사용합니다.
- 사용자에게 보이는 기능은 동작만 연결하지 않고 버튼 배치, 간격, 문구, 툴팁, 모달, 반응형, 접근성, 캐시 키까지 함께 완성하고 실제 브라우저에서 확인합니다.
- 동작·수치·상태를 바꾸면 관련 설명, source/generated seed, 회귀 검사와 현재 문서를 전수 검색해 동기화합니다.
- 파괴적 동작은 브라우저 기본 `alert`/`confirm` 대신 게임 UI와 일관된 확인 모달을 사용하며 실행 전 영향과 반환값을 보여줍니다.
- 코드나 구조를 바꾸면 관련 focused smoke, Python compileall, JavaScript syntax와 `bash tools/run_smoke_core.sh`를 위험도에 맞게 검증합니다. Vue를 바꾼 경우에만 `frontend/vue-app`에서 `.venv` 없이 `npm ci`와 `npm run build`를 실행합니다.
- 기존 사용자 변경이 공백·들여쓰기·정렬만 바꾼 비기능 포맷 변경임을 기계적으로 확인한 경우에는 별도 보존하지 않고 현재 작업과 함께 commit할 수 있습니다. 선택자·속성·값·실행 토큰이 달라지면 사용자 기능 변경으로 분리해 보존합니다.

## 로컬 자원과 안전 경계

- 숨김 파일과 ignored `.env`는 점검·수정할 수 있지만 실제 secret, token, PAT, password, CA, cert, key를 Git·채팅·로그·artifact에 노출하지 않습니다.
- 실제 local/Neon DB write, reset, restore, seed, Alembic apply·stamp·downgrade, Docker container/network/volume 변경, GHCR 게시, Render env·deploy는 해당 단계와 exact 범위를 별도 확인한 뒤 실행합니다.
- root `.dockerignore`는 `.env` 계열을 전부 제외합니다. 나중에 회전할 항목은 `docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md`에 기록합니다.
- 현재 고정 GitHub/GHCR namespace는 `gihohoho`, repository는 `ghcr.io/gihohoho/upgrade-rpg-backend`, target은 `linux/amd64`입니다. placeholder로 되돌리지 않습니다.
- GitHub Actions 게시 모델은 `owner-only-source-controlled-two-step`이며 production image는 exact digest만 사용합니다.

## 계정·인증·캐릭터

- 시작 순서는 로그인/가입 → 계정별 캐릭터 슬롯 8개 → 캐릭터 선택/생성 → 해당 저장 로드입니다. 인증과 캐릭터 선택 전에는 게임 boot와 자동 저장을 시작하지 않습니다.
- 슬롯은 `character-1`부터 `character-8`, 캐릭터 식별자는 슬롯과 별개의 32자리 `accountCharacterId`입니다. Bearer 계정, 슬롯 키, 캐릭터 ID가 모두 일치해야 저장·로드합니다.
- 서버 snapshot이 정상 load의 기준입니다. 다른 local은 복구 백업으로 보존하며, `pending-unsynced` 충돌은 사용자가 local/server 중 하나를 명시적으로 선택하기 전까지 자동 덮어쓰지 않습니다.
- 자동·수동·전환 저장은 하나의 직렬 큐를 사용합니다. 전환 시 runtime과 전투 timer를 먼저 멈추고 최종 저장을 기다린 뒤 token과 선택 상태를 지웁니다.
- `401/403`은 local과 pending marker를 보존하고 재로그인으로 돌립니다. network/timeout/`5xx`는 token을 보존하고 재시도합니다.
- 신규 가입은 아이디와 필수 이메일을 받으며 이메일 인증 전에는 로그인할 수 없습니다. 아이디 찾기, 비밀번호 재설정, 인증 재전송, 계정 삭제 메일은 계정 존재 여부를 공개 응답에서 숨깁니다.
- 이메일 action token은 원문을 저장하지 않고 `EMAIL_TOKEN_SECRET` HMAC digest만 저장합니다. JWT `authVersion` 불일치, 정지·미인증 계정은 매 요청에서 차단합니다.
- 인증 `422`는 `loc`, `type`, `msg`만 반환합니다. 비밀번호·token·요청 body와 SQL bind parameter를 응답·로그에 남기지 않습니다.
- 회원가입은 관리자 권한을 만들지 않습니다. owner bootstrap은 별도 one-shot, exact SHA, clean tracked tree, 기존 관리자 0명, 명시 확인을 모두 요구하며 성공 뒤 평문 password env를 제거합니다.
- 공개 회원가입 전 rate limit, ASGI raw body cap, durable mail queue/timing 보호, 미인증 계정 회수, server session/revoke, save revision 충돌, CSP/XSS, 개인정보 정책을 완료해야 합니다.

상세 계약은 [계정·캐릭터 슬롯](docs/current/ACCOUNT_AUTH_AND_CHARACTER_SLOTS.md)과 [이메일 인증·복구·삭제](docs/current/ACCOUNT_EMAIL_VERIFICATION_RECOVERY_AND_DELETION.md)를 따릅니다.

## UI·아이템·이미지 규칙

- 인벤토리·보관함·휴지통은 이동·사용 뒤 빈 칸을 유지합니다. 새 아이템은 첫 빈 칸을 쓰고 `위로 정렬` 버튼을 눌렀을 때만 상대 순서를 유지해 압축합니다.
- 이미지 파일은 동일한 정사각형 full-bleed PNG이며 내부 테두리·카드판·글자·키 문자·희귀도 프레임을 넣지 않습니다. 아이템 등급 테두리는 모든 UI 위치에서 CSS로 일관되게 적용합니다.
- 장비 계열 상위 이미지는 기본형을 직접 편집해 실루엣·각도·정체성을 유지하고 재질·룬·효과만 단계적으로 발전시킵니다. 이름 포함 관계와 확정 tier 표를 함께 사용합니다.
- 스킬 아이콘은 작은 슬롯에서도 읽히는 단일 문양 중심입니다. 기본 자동/패시브는 초록, 버프는 파랑, 액티브는 노랑, `SQ`·`SW`·`M`은 보라 계열입니다.
- 스킬강화권은 `Q → W → E → R → T → F → D → SQ → SW → M` 한 계열이며 직전 이미지를 직접 편집해 발전시킵니다.
- 자산별 상세 매핑과 승인 기준은 [자산 reference](docs/reference/assets/SPECIAL_EQUIPMENT_AI_ICON_ASSETS.md)를 우선합니다.

## 문서 체계

- `docs/current/`: 지금 판단과 승인에 필요한 소수의 문서
- `docs/reference/`: 계속 유효한 주제별 기술 자료
- `docs/generated/`: checker/report가 다시 만드는 결과물; 직접 편집 금지
- `docs/contracts/`: API와 관리자 계약
- `docs/guides/`: 실행 절차
- `docs/archive/history/`: 완료된 단계의 검색용 통합 역사; 현재 규칙으로 사용 금지
- 같은 내용을 여러 파일에 복사하지 않습니다. 새 채팅용 상태는 `NEXT_CHAT_HANDOFF.md` 한 곳에 기록하고 `NEXT_CHAT_PROMPT.md`는 그 문서를 가리키는 짧은 안내만 유지합니다.
- 구조를 바꾸면 [Docs Hub](docs/README.md), [Current Index](docs/current/README.md), [Documentation System](docs/DOCUMENTATION_SYSTEM.md), 문서 구조 smoke와 root handoff를 함께 갱신합니다.
- 작업 종료 문서 마감 절차는 [Documentation System](docs/DOCUMENTATION_SYSTEM.md)을 따릅니다. 개인 `.obsidian/` 설정은 Git에 commit하지 않고 Codex가 로컬에서 관리합니다.

## 현재 체크포인트

```txt
latest: v379.vue-typescript-pinia-foundation
strict result: vue-typescript-pinia-foundation
next safe stage: migrate-vue-auth-character-gate
local source head: v377_auth_email_public_security
local/Neon DB current: v377_auth_email_public_security / v377_auth_email_public_security
v377 apply/stamp/downgrade: local 1/0/0; Neon 1/0/0
email rollout approval/execution: yes/public-live
public backend/static: v377/v378 Live
Render public preview: deployed
production approval/execution: yes/yes
v378 production approval/execution: yes/yes
v379 production approval/execution: no/no
```

- v379에서 `frontend/vue-app`을 전체 프론트엔드 전환 작업공간으로 전환하고 새 Vue 기반에 TypeScript, Pinia, typed Router entry, 반응형 공통 layout과 접근성 기본 규칙을 적용했습니다. 기존 legacy 공개 화면·backend·DB·secret·배포는 변경하지 않았습니다.
- Vue v379 `npm ci`, `vue-tsc`, production build, Vue focused smoke와 실제 desktop/mobile browser 검증이 PASS했습니다. 다음은 로그인·이메일 인증·캐릭터 슬롯 gate의 Vue 이식이며 production 관리자 복구는 별도 DB-write 승인 전까지 보류합니다.
- v378 legacy static은 승인 SHA `c56525394a4099160e7a32e93dc2d3a0d54568b3`에서 Render deploy `dep-da5vn3m417fc738rs2bg`로 정확히 1회 배포되어 live입니다. backend·DB·secret은 변경하지 않았습니다.
- v371 source는 이메일 인증·복구·삭제, `authVersion`, Brevo HTTPS renderer/transport, owner bootstrap과 migration source를 준비했습니다.
- v372는 기능을 바꾸지 않고 Markdown 243개를 95개로 정리하고 `docs/current`의 실제 현재 문서를 11개로 줄였습니다. entry/current/reference/generated/archive 역할과 구조 smoke를 고정했습니다.
- v373은 승인된 `email-validator==2.3.0`과 전이 의존성 `dnspython==2.8.0`을 backend `.venv`와 재현 가능한 Linux runtime/dev lock에 반영했습니다. dependency가 임의로 빠지면 이메일 동작은 계속 503으로 fail-closed합니다.
- Obsidian 1.13.7에서 저장소 루트를 `Upgrade RPG` local vault로 등록하고 ignored `.obsidian/` 설정과 핵심 문서·색인의 표준 Markdown 링크를 연결했습니다. Obsidian은 로컬 탐색기이며 Git source of truth를 대체하지 않습니다.
- Linux lock check, `pip check`, email normalize/import-failure 503, v371/v370 focused, GHCR 재현성, compileall, blocking-I/O, 문서 구조와 전체 core smoke가 PASS했습니다.
- v374는 루트 README에 최초 준비·DB/backend/legacy/Vue·확인 URL·안전 종료를 위치/`.venv`/설치 상태와 함께 통합하고, Obsidian Graph·Local Graph·Backlinks·Bookmarks의 실제 사용법을 문서화했습니다.
- v375는 사용자용 Obsidian 사용 설명을 추적 문서에서 제거하고, ignored 로컬 vault의 북마크·저장 검색·전역/로컬 Graph·workspace를 Codex가 직접 관리하도록 전환했습니다. 의미가 동일한 `src/styles/style.css` 포맷 정렬도 검증 뒤 함께 반영합니다.
- Obsidian 1.13.7 재실행 뒤 북마크 8개, Graph 색상 그룹 13개, Local Graph 깊이 3과 필수 pane을 확인했고, CSS PostCSS AST 동등성·문서/정적 배포 focused·전체 core smoke가 PASS했습니다.
- v376에서 실행 환경 사전 고정, 범위별 단일 검증, 성공 후 중복 확인 금지와 작업별 자체 피드백을 영구 규칙으로 추가했습니다. 기호는 실질적인 이메일 인증 rollout에 필요한 보안 구현·migration·provider 설정·테스트 메일·배포를 승인했습니다.
- README 명령 계약·위험 명령 차단·Markdown 링크/중복/크기와 handoff readiness가 PASS했고, 현재 legacy 게임/관리자 HTTP 200과 기존 PostgreSQL healthy를 읽기 전용으로 확인했습니다.
- Brevo local 계정·발신자·API key와 실제 메일 인증은 완료했습니다. owner bootstrap, Render secret, 새 image/static 배포는 실행하지 않았습니다.
- v377 source는 PostgreSQL HMAC rate limit, auth IP 사전 보호, JSON 파싱 전 body cap, semantic mail outbox, 안전한 미인증 identity 회수와 202/429/413 frontend 계약을 추가했습니다.
- v377 focused 검사와 설치된 Git Bash·backend `.venv`·`DEBUG=false` 조건의 전체 core smoke가 PASS했습니다.
- private environment 준비는 535개 기존 artifact의 ACL을 비공개로 고정하고 local/production에 서로 다른 email/abuse secret 4개를 값 출력 없이 생성해 완료했습니다. local Brevo key와 검증된 발신자는 ignored `backend/.env`에 값 출력 없이 준비했고 Render에는 아직 전달하지 않았습니다.
- `8db9bcb`에서 synthetic isolated v295→v377→v295→v377과 local v295 custom backup 751 rows가 성공했지만, fingerprint canonicalization source 수정 뒤에는 둘 다 현재 SHA에 사용할 수 없는 stale evidence입니다.
- 첫 local apply는 Alembic 실행 전에 cross-driver fingerprint 표현 차이를 실제 차이로 잘못 판정해 안전 중단됐습니다. apply report는 없고 local DB는 v295 그대로이며 attempt marker를 보존하므로 같은 action을 재실행하지 않습니다. Neon은 접속·backup·apply·marker가 모두 없습니다.
- aware datetime과 Decimal fingerprint를 driver-independent하게 canonicalize했고 실제 local 751행의 asyncpg/psycopg read-only parity가 PASS했습니다. 이 source 수정으로 `8db9bcb` evidence는 현재 SHA에 stale입니다.
- `345872a`의 `recovery1`에서 local DB를 v377로 정확히 1회 upgrade했고, 최종 `recovery2`에서는 synthetic 왕복과 Neon fresh backup 뒤 Neon을 v377로 정확히 1회 upgrade했습니다. 두 실제 DB 모두 기존 22개 table 데이터 변화 0과 25개 model table parity를 확인했습니다.
- v295에서 생성된 이메일 없는 기존 계정은 아이디·비밀번호 로그인을 계속 허용하되 `emailVerified=false`로 정직하게 표시합니다. 이메일이 있는 신규 계정은 링크 인증 전 계속 차단합니다.
- Brevo 전용 API key·검증된 sender·anonymous tracking·1개월 log retention·preview 미저장을 local 범위에서 준비했고, 실제 Naver 메일 수신→링크 인증→로그인→8개 캐릭터 슬롯 진입을 확인했습니다. key와 sender 값은 ignored `backend/.env`에만 있으며 Render에는 넣지 않았습니다.
- `delivery_outcome_unknown`은 Brevo 장애가 아니라 여러 로컬 reload worker가 겹친 실행 환경에서 provider 수락 뒤 worker ownership이 끊긴 안전 종료였습니다. 단일 직접 provider 진단은 2초 이내 message ID를 반환했고 production image는 reload 없이 worker 1개를 유지합니다.
- 기존 recovery1 증거와 marker를 보존한 채 `recovery2` isolated 왕복·Neon backup·Neon apply를 각각 1회 완료했습니다. reset·seed·restore·stamp·actual downgrade와 자동 retry는 실행하지 않았습니다.
- GitHub Actions run `32576889295`의 단일 attempt가 새 signed digest `sha256:a91d020c6b8abfbbcca56c1ff3ff7736c155fd43d854398e42bb0e42450ec994`를 게시했고, Render backend deploy `dep-da4qqi3tqb8s738l68h0`와 static deploy `dep-da4qr867bikc73aekck0`이 live입니다.
- Render에는 필수 email/security 환경변수 35개가 값 노출 없이 준비됐습니다. 공개 health는 HTTP 200이고 auth schema 오류는 422, 허용된 Naver 테스트 주소의 인증메일 재요청은 generic 202와 `Cache-Control: no-store`를 반환했습니다.
- 공개 회원가입·새 이미지 배포 blocker는 server session/revoke, save CAS, CSP/XSS·브라우저 token, 개인정보 정책입니다. 이메일 rollout 내에서도 이 gate를 우회하지 않습니다.
- 검증된 공개 주소는 `https://gihohoho-upgrade-rpg.onrender.com/index.html`, `/admin.html`, backend는 `https://upgrade-rpg-api.onrender.com`입니다.
- 이전 배포·콘텐츠·이미지의 상세 이력은 `docs/archive/history/`와 Git history에서 필요할 때만 확인합니다.
