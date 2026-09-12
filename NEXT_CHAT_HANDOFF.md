# Upgrade RPG Codex handoff — v400

새 채팅은 루트 [AGENTS.md](AGENTS.md)를 먼저 읽고 이 문서를 이어서 사용합니다. 더 자세한 현재 상태는 [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)가 기준입니다.

```txt
latest: v401.legacy-live-game-improvements
strict result: legacy-live-game-improvements
next safe stage: await-user-vue-resume
source head: v377_auth_email_public_security
local/Neon DB current: v377_auth_email_public_security / v377_auth_email_public_security
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

## 이번 체크포인트

- v401 사용자 요청 5개를 구현하고 SHA `a86fd0c2c9c31516a73cf6de352dc6f34a67851d`로 배포했습니다. deploy `dep-daih3krm8hqs73crb140` Live, 공개 변경 파일 7개 bytes 일치와 최신 API 기반 45종 회귀 PASS입니다. Vue는 계속 중단합니다. 사용한도 중단 시 남은 단계부터 재개하고 성공한 검사는 반복하지 않습니다.

- 사용자가 Vue 작업을 일시 중단하고 실서버 일반·특수보스 드랍 수정과 배포를 승인했습니다. v400은 `src/api/master-data-adapter.js`에서 보정된 확률 4종·드랍 제목·보정 marker를 복구하고 `index.html` 캐시 키를 `v=400`으로 변경합니다. 배포 상태와 검증 증거는 [현재 상태](docs/current/CURRENT_STATUS.md)의 v400 절을 따릅니다.
- Render 로그인·브라우저 연결 복구 후 SHA `6652e41ceb50edc077414d0b8d3a531c27b6df7f`를 static service `srv-d9iu337aqgkc73am4lh0`에 정확히 1회 배포했습니다. deploy `dep-dai1u8mq1p3s73anmmi0`은 Live이며 공개 파일 bytes 대조·배포 코드 지급 회귀·브라우저 드랍표 검증 PASS입니다. 반복 배포하지 않습니다.
- v399는 가방↔보관함 묶음 이동과 정렬 적용을 연결합니다. 순수 `transferItemSlot`이 source의 빈 칸·ID·강화·수량·추가 필드를 유지하고 destination 첫 빈 칸을 사용합니다. 자동 합치기는 아직 하지 않습니다.
- 전체 Vue smoke·TypeScript·production build PASS. 1366px/390px synthetic 브라우저에서 양방향 이동·정렬 저장·503 실패/재시도·pending 해제·가로 넘침 0·console error 0을 확인했고 임시 fixture는 제거했습니다.
- store는 prospective snapshot의 복구본 기록이 성공해야 화면을 바꾸고 공통 queue에 저장합니다. quota/다른 탭 변경은 변경 전 차단합니다. 저장 실패는 pending을 보존하며 재시도는 이동을 반복하지 않습니다. 저장 중/오류/전환 중 후속 변경을 잠그고 401/403은 로그인으로 돌아갑니다.
- 가방·보관함 정렬은 미리보기 후 `정렬 적용·저장`으로 확정합니다. 휴지통 정렬은 미리보기만 유지합니다. 장착·사용·판매·자동 합치기·휴지통 이동/복구/삭제·Gold·보상·난수는 연결하지 않았습니다.
- v398의 실제 보유 snapshot 표시·전체 칸·중복 선택·아이콘, v397의 계정/슬롯/캐릭터별 pending 복구 선택과 v396의 13px typography·좌우 창·공유 modal 접근성을 유지합니다.
- Vue v399 검증은 메모리 저장소·가짜 API만 사용했고 Vue 서버만 npm ci 뒤 재시작했습니다. 이후 v400/v401은 사용자 승인으로 공개 legacy static만 배포했으며 DB·backend·env·secret은 유지했습니다.
- 공개 backend v377/static v401이 Live이며 Vue v379~v399는 미배포입니다. DB migration/메일/배포 상세 증거는 [현재 상태](docs/current/CURRENT_STATUS.md)를 따르고 재실행하지 않습니다.
- 관리자 Preview는 Bearer/isAdmin과 `dryRun: true`이며 Apply/재인증/dev key header는 잠겼습니다. production `admin` 승격/owner bootstrap도 별도 exact DB-write 승인 전까지 실행하지 않습니다.
- `saveVersion`은 형식 버전이며 backend CAS는 미구현입니다. 다중 탭 localStorage 비교도 원자적 CAS가 아닙니다. legacy 키 자동 가져오기/삭제·복구본 자동 정리/다운로드는 제공하지 않습니다.

## 바로 할 일

1. `await-user-vue-resume`: v401 구현·검증·배포를 완료했습니다. 기존 접속 게임은 새로고침해야 새 코드를 읽습니다. 배포/검사를 반복하지 말고 사용자 후속 요청을 기다립니다. 브라우저 종료·탭 폐기 뒤 오프라인 사냥은 지원 범위가 아닙니다.
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
