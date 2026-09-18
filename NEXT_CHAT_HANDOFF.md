# Upgrade RPG Codex handoff — v402 배포 준비 완료

새 채팅은 루트 [AGENTS.md](AGENTS.md)를 먼저 읽고 이 문서를 이어서 사용합니다. 더 자세한 현재 상태는 [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)가 기준입니다.

## 중요: 크레딧 소진 후 즉시 이어갈 작업

- 사용자 기호는 **서버 사냥·강화 확정 구조 구현과 실제 배포를 승인**했습니다. 사용량 한도 때문에 중단되면 아래 남은 단계부터 이어갑니다. 별도 재승인을 반복해서 묻지 않습니다. Vue v399 작업은 계속 중단합니다.
- 목표: 로그인한 게임 탭의 살아 있는 연결에 한해 60초 단위 서버 사냥/보상 저장. 알트탭은 허용, 탭 종료·오프라인 시간은 제외. 중요한 행동 직전까지 사냥 정산 후 재료·골드 차감/난수 결과/요청 영수증을 한 DB 트랜잭션으로 저장하고 결과를 표시합니다. 같은 요청 재시도는 재추첨하지 않습니다. 브라우저 전체 snapshot 저장 우회도 차단합니다.
- 함께 완료할 항목: 다른 보스 선택 차단은 모달 안내; 초보자 장비를 보스 장비로 교체; 4번 스태프/6번 창/5번 공용; 낮은 아이템 레벨 우선 교체, 동률이면 5번 마지막. 기존 잘못된 칸의 장비는 가방/우편으로 안전하게 반환합니다.
- **9월 16일 추가 요청:** 24시간 자동 로그아웃을 완전히 제거합니다. TTL 0은 시간 만료 없음(`expiresIn: 0`, 서명된 `sessionLifetime: until-revoked`), 계정 정지/비밀번호 재설정 `authVersion` 검사와 명시 로그아웃은 유지합니다. 게임 탭 종료/오프라인 사냥 금지는 로그인 유지와 별개입니다. 실제 Render 환경의 `ACCESS_TOKEN_EXPIRE_MINUTES`도 0으로 바꿔야 합니다. 이미 만료된 토큰은 복구하지 않습니다.
- **2026-09-19: 첫 게시가 보안 검사에서 차단돼 OS 수정 preparation을 준비했습니다.** 기호는 `74435a27ea1dc61cd487f77726def49198194173`를 정확히 승인했습니다. authorization `8fdf8a03033e07cc6b73f9bc3f00474b20e78a49` → run `35367950275` 1회 → 즉시 closure `37167199e0aa7346140d6685542e6240f6c05fb4` → 실패 record `9aad11606014d178fcc9b6a8f747731eaa31fdc3`를 push했습니다. CI repository checks/전체 core/build PASS, OS HIGH 10건 때문에 publish skipped입니다. GHCR login/push·Neon apply·Render env/deploy는 없고 같은 run 재실행은 금지입니다.
- 원인/수정: Alpine libcrypto3/libssl3 `3.5.7-r0→3.5.8-r0`, libuuid `2.41.4-r0→2.41.6-r1`, sqlite-libs `3.51.2-r0→3.53.4-r0`. 기존 base digest와 Python/게임 코드는 유지하고 runtime에서 4개 보안 버전을 고정합니다. 새 이미지 build/엔진 실행 PASS, CI와 같은 Trivy 0.70.0·HIGH/CRITICAL·미수정 포함 검사 0건 PASS. artifact `10556663877`와 로컬 `local-review-artifacts/v402-patched-scan/`를 보존합니다. 새 preparation SHA의 정확한 확인 뒤 새 단일 게시부터 재개합니다.
- **local v402 적용 완료: 재실행 금지.** source `3716719`, fresh private backup/TOC, apply 1/stamp 0/downgrade 0, 기존 25개 테이블 783행 fingerprint 변화 0, 27개 model parity PASS. `local-backups/postgres/v402/local.completed.json`이 기준입니다. Neon은 v377/25개 table이며 새 이미지 게시 성공 후 Neon만 적용합니다.

- 구현: QuickJS(`quickjs-ng==0.16.2.1`)로 기존 신뢰된 JS 전투/강화 규칙 실행, 세션 연결/행 잠금/요청 영수증/난수 커서 저장. raw snapshot 저장 우회 차단, 서버 기준 60초 정산, 45초 연결 유예, 오프라인 시간 제외, 재연결 시 기존 전투 복원입니다. 브라우저 화면은 예상 진행을 보여주고 확정 보상은 서버 응답으로 반영합니다.
- 시간 만료 없는 로그인은 서명·계정 활성·`authVersion` 검사를 유지합니다. 기존 유효한 24시간 토큰은 게임 연결 때 교환합니다. 이미 만료된 사용자는 배포 후 한 번 재로그인해야 합니다. 이메일 인증 링크의 24시간 만료는 별개로 유지합니다.
- **PASS:** 전체 core(실패한 기존 버전/역사 fixture만 수정 후 해당 줄부터 재개), 엔진 8개 회귀/45종 보스, 무기칸·우편·난수·60초 동등성, PostgreSQL 격리 schema의 중복 요청/rollback/응답 유실/24시간 오프라인 제외, 로그인 시간 경과·계정 폐기, 추가 묶음 강화 후 선택 대상 회귀, Ruff/compileall/JS syntax입니다. 마지막 선택 UI 보완은 관련 회귀만 검사하며 full core를 반복하지 않습니다.
- **실제 브라우저 PASS:** 초보자 장비 교체, 강화 중 표시, commit 후 503와 동일 결과 재조회(골드/아이템/영수증 중복 없음), 다른 보스 제거 안내 모달, 소환 자동/드랍 ON, 다른 탭 동안 보스 처치 45→91 및 revision 증가. 1366/390px 새 모달은 화면 안에 맞고 버튼 44px, console error 0. 기존 모바일 게임 본체의 가로 넘침은 이번 변경 범위 밖이며 해결했다고 기록하지 않습니다.
- production Linux/amd64 Docker build 및 QuickJS 실행 PASS. lock 3개에는 QuickJS만 추가했습니다. `tools/apply_v402_server_gameplay.py`는 private backup+TOC 검증, exact clean/pushed SHA, 시도 1회 marker, 기존 25개 테이블 fingerprint 보존 및 27개 model parity를 같은 transaction에서 확인합니다. 동일 적용 함수를 synthetic schema와 실제 local에서 검증했습니다. Neon은 미적용입니다.
- **배포 순서:** (1) 사용자 exact preparation SHA 확인 → GitHub owner/main/Actions 설정 읽기 확인 → lifecycle 단일 파일 authorization 직계 자식 commit/push → workflow 1회 dispatch, 즉시 closure commit, run/digest/signature 기록 (2) Neon만 backup 후 `apply_v402_server_gameplay.py --target neon --apply --source-sha <그 시점의 clean pushed HEAD>` 1회 (3) 새 backend exact digest + `ACCESS_TOKEN_EXPIRE_MINUTES=0`, `GAME_SERVER_AUTHORITY_ENABLED=false`로 먼저 배포 (4) v402 static 배포 후 서버 flag true로 활성화 (5) 공개 상태 확인·문서 마감·commit/push. 실제 실패 시 무조건 재실행하지 말고 marker와 응답을 먼저 확인합니다.
- 새 lifecycle은 `preparation-closed`, gate false, owner approval false, 이전 완료 시도 12회 보존입니다. 기존 workflow의 `.github/workflows/publish-backend-ghcr.yml`은 `ownerApproval.evidence == "exact-40-character-sha-user-message"`를 요구합니다. 최초 SHA 승인은 기록했고 보안 수정으로 달라진 새 SHA의 확인은 아직입니다.
- 검증 fixture는 ignored `local-review-artifacts/v402_browser_fixture.py`에서 synthetic schema를 만들며 `http://127.0.0.1:8000/__review/finish`로 서버와 schema를 정리합니다. 9월 18일 정상 종료(exit 0)와 브라우저 정리를 마쳤습니다. 테스트 계정/토큰은 실제 계정과 분리합니다. 기록은 `v402-core*.log`, `v402-image-final.log`이며 secret은 포함하지 않습니다. 사용자 데이터 reset/seed/restore/stamp/downgrade, owner bootstrap은 범위 밖입니다.
- 이번 보안 수정의 기준 HEAD는 실패 record `9aad116`이며 게임 구현은 승인된 `74435a2`와 같습니다. 기존 v401 static deploy `dep-daih3krm8hqs73crb140`은 rollback 기준이며 반복 배포하지 않습니다.

```txt
latest: v402.server-gameplay-prepared
strict result: server-gameplay-prepared
next safe stage: approve-v402-release-preparation
source head: v402_server_gameplay
local/Neon DB current: v402_server_gameplay / v377_auth_email_public_security
v377 apply/stamp/downgrade: local 1/0/0; Neon 1/0/0
email rollout approval/execution: yes/public-live
public backend/static: v377/v401 Live
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

## 직전 완료 체크포인트

- 공개 backend/static은 v377/v401 Live입니다. v401 SHA `a86fd0c2c9c31516a73cf6de352dc6f34a67851d`, deploy `dep-daih3krm8hqs73crb140`: 45종 보스·공개 bytes·core·브라우저 PASS. 반복 배포하지 않습니다.
- Vue v399는 가방↔보관함 이동/정렬 저장, 복구본 선기록, 같은 snapshot 재시도까지 완료·미배포입니다. 장착/사용/합치기는 연결하지 않았습니다. 다음 Vue 작업은 사용자 재개 뒤 `migrate-vue-game-stack-merge-foundation`입니다.
- 계정/캐릭터별 local·pending은 보존합니다. 관리자 Apply/owner bootstrap은 별도 범위입니다. 이전 migration·이메일·배포 증거는 [현재 상태](docs/current/CURRENT_STATUS.md)를 따릅니다.

## 바로 할 일

1. `approve-v402-release-preparation`: 위 중요 절의 exact preparation SHA 확인 뒤 게시·배포부터 이어갑니다. 이미 PASS한 검사는 변경과 무관하면 반복하지 않습니다.
2. Vue 작업은 일시 중단 상태입니다. 사용자 재개 요청 후에만 `migrate-vue-game-stack-merge-foundation`을 진행합니다. 수량·강화·옵션 보존과 가득 찬 목적지 합치기를 확인할 계획을 유지합니다.
3. 실제 관리자 Apply API, 비밀번호 재인증 request, dev key header와 DB write는 연결하지 않습니다. 진행하려면 작업 종류와 exact DB-write 범위를 별도로 승인받습니다.
4. production 관리자 복구는 Vue 화면 이식과 분리하며 기존 `admin` 승격 또는 새 owner 생성의 exact DB-write 승인을 받기 전에는 실행하지 않습니다.

## 안전 경계

- 실제 secret·token·password·DB URL·메일 본문은 출력·문서·Git artifact에 남기지 않습니다.
- 완료된 migration, GitHub Actions, Render backend/static deploy를 단순 확인 목적으로 다시 실행하지 않습니다.
- owner bootstrap, DB reset·seed·restore·stamp·actual downgrade, production 자동 retry는 별도 승인 없이는 실행하지 않습니다.
- 기호가 승인한 이메일 인증 rollout은 완료됐지만 남은 공개 계정 gate를 우회하는 승인은 아닙니다.

## 문서 기준

- 현재 판단: `docs/current/`
- 장기 기술 자료: `docs/reference/`
- 자동 생성 보고서: `docs/generated/`
- API 계약: `docs/contracts/`
- 실행 안내: `docs/guides/`
- 완료 이력: `docs/archive/history/`

문서 체계는 [Documentation System](docs/DOCUMENTATION_SYSTEM.md), 전체 색인은 [Docs Hub](docs/README.md)가 기준입니다.
