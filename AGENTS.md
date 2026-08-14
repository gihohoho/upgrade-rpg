# Upgrade RPG Codex working rules — v374

이 파일은 저장소 전체에 적용되는 **장기 규칙**입니다. 새 작업은 다음 순서로 시작합니다.

1. [AGENTS.md](AGENTS.md)
2. [NEXT_CHAT_HANDOFF.md](NEXT_CHAT_HANDOFF.md)
3. [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)
4. 작업과 직접 관련된 `docs/current/`, `docs/reference/`, `docs/contracts/` 문서

과거 구현 세부는 처음부터 읽지 않고 필요할 때만 `docs/archive/history/`에서 검색합니다.

## 사용자와 작업 방식

- 사용자는 코딩을 거의 모르는 **기호**입니다. 항상 쉽고 구체적인 한국어로 설명합니다.
- 모든 터미널 명령 바로 위에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적습니다.
- backend 가상환경은 `backend/.venv`입니다. Git Bash에서는 `backend`에서 `source .venv/Scripts/activate`로 켭니다.
- Vue/npm은 `frontend/vue-app`에서 실행하며 Python `.venv`가 필요 없습니다.
- 필요한 extension, 권한, 설치, 외부 계정 작업이 있으면 기호에게 요청하고 해결될 때까지 handoff에 남깁니다.
- Codex는 정상 실행 중인 backend `127.0.0.1:8000`, Vue `127.0.0.1:5173`, legacy static `127.0.0.1:5500` 서버를 재사용합니다.
- legacy 브라우저 검증은 `http://127.0.0.1:5500/index.html`과 `/admin.html`을 사용합니다. `file://`는 사용하지 않습니다.
- Windows 전역 `DEBUG=release`는 backend 설정과 충돌하므로 backend 검사 자식 프로세스에서만 `DEBUG=false`로 덮어씁니다.
- 변경·검증 뒤 Codex가 직접 `git status`, 선택적 stage, commit, push를 수행합니다. 사용자 변경은 stage하지 않습니다. ZIP과 Git 명령 안내는 요청받지 않는 한 제공하지 않습니다.
- 서버를 재시작하지 않았으면 완료 답변에 `서버 재시작 불필요`라고 적습니다.
- 모든 작업의 마지막에는 [AGENTS.md](AGENTS.md), [NEXT_CHAT_HANDOFF.md](NEXT_CHAT_HANDOFF.md), [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)를 현재 상태와 맞추고, 변경 주제와 관련된 Markdown을 전수 검색해 통합·이동·archive·삭제 필요 여부까지 점검합니다. 의미 없는 복사본이나 단계별 새 문서를 만들지 않습니다.

## 변경 품질

- 새 추상화·의존성·파일보다 기존 코드와 표준 기능을 먼저 사용합니다.
- 사용자에게 보이는 기능은 동작만 연결하지 않고 버튼 배치, 간격, 문구, 툴팁, 모달, 반응형, 접근성, 캐시 키까지 함께 완성하고 실제 브라우저에서 확인합니다.
- 동작·수치·상태를 바꾸면 관련 설명, source/generated seed, 회귀 검사와 현재 문서를 전수 검색해 동기화합니다.
- 파괴적 동작은 브라우저 기본 `alert`/`confirm` 대신 게임 UI와 일관된 확인 모달을 사용하며 실행 전 영향과 반환값을 보여줍니다.
- 코드나 구조를 바꾸면 관련 focused smoke, Python compileall, JavaScript syntax와 `bash tools/run_smoke_core.sh`를 위험도에 맞게 검증합니다. Vue를 바꾼 경우에만 `frontend/vue-app`에서 `.venv` 없이 `npm ci`와 `npm run build`를 실행합니다.

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
- Obsidian은 설치된 로컬 지식 탐색기로 사용합니다. 저장소 루트를 vault로 열고 표준 Markdown 링크·Backlinks·Graph·Search를 사용하되, 프로젝트와 Codex는 Obsidian 없이도 동일하게 동작해야 합니다. 개인 `.obsidian/` 설정과 community plugin은 commit하지 않습니다.
- 작업 종료 문서 마감 절차와 Obsidian 검색·제외 경로는 [Documentation System](docs/DOCUMENTATION_SYSTEM.md)을 따릅니다.

## 현재 체크포인트

```txt
latest: v374.local-run-readme-obsidian-usage-ready
strict result: local-run-readme-obsidian-usage-ready
next safe stage: owner-review-v371-migration-source-and-approve-isolated-roundtrip
local source head: v371_email_identity_lifecycle
local/Neon DB current: v295_initial_schema
v371 migration applied: no
public backend/static: v351 Live
Render public preview: deployed
production approval/execution: no/no
```

- v371 source는 이메일 인증·복구·삭제, `authVersion`, Brevo HTTPS renderer/transport, owner bootstrap과 migration source를 준비했습니다.
- v372는 기능을 바꾸지 않고 Markdown 243개를 95개로 정리하고 `docs/current`의 실제 현재 문서를 11개로 줄였습니다. entry/current/reference/generated/archive 역할과 구조 smoke를 고정했습니다.
- v373은 승인된 `email-validator==2.3.0`과 전이 의존성 `dnspython==2.8.0`을 backend `.venv`와 재현 가능한 Linux runtime/dev lock에 반영했습니다. dependency가 임의로 빠지면 이메일 동작은 계속 503으로 fail-closed합니다.
- Obsidian 1.13.7에서 저장소 루트를 `Upgrade RPG` local vault로 등록하고 ignored `.obsidian/` 설정과 핵심 문서·색인의 표준 Markdown 링크를 연결했습니다. Obsidian은 로컬 탐색기이며 Git source of truth를 대체하지 않습니다.
- Linux lock check, `pip check`, email normalize/import-failure 503, v371/v370 focused, GHCR 재현성, compileall, blocking-I/O, 문서 구조와 전체 core smoke가 PASS했습니다.
- v374는 루트 README에 최초 준비·DB/backend/legacy/Vue·확인 URL·안전 종료를 위치/`.venv`/설치 상태와 함께 통합하고, Obsidian Graph·Local Graph·Backlinks·Bookmarks의 실제 사용법을 문서화했습니다.
- README 명령 계약·위험 명령 차단·Markdown 링크/중복/크기와 handoff readiness가 PASS했고, 현재 legacy 게임/관리자 HTTP 200과 기존 PostgreSQL healthy를 읽기 전용으로 확인했습니다.
- Brevo 계정·발신자·API key·secret, 실제 메일, DB migration, owner bootstrap, 새 image/static 배포는 실행하지 않았습니다.
- source-prepared 즉시 수정 blocker는 없습니다. 공개 배포 blocker는 rate limit/queue/body cap, 미인증 계정 회수, session/revoke, save CAS, CSP/XSS·개인정보 정책입니다.
- 검증된 공개 주소는 `https://gihohoho-upgrade-rpg.onrender.com/index.html`, `/admin.html`, backend는 `https://upgrade-rpg-api.onrender.com`입니다.
- 이전 배포·콘텐츠·이미지의 상세 이력은 `docs/archive/history/`와 Git history에서 필요할 때만 확인합니다.
