# Upgrade RPG Codex handoff — v399

새 채팅은 루트 [AGENTS.md](AGENTS.md)를 먼저 읽고 이 문서를 이어서 사용합니다. 더 자세한 현재 상태는 [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)가 기준입니다.

```txt
latest: v399.vue-game-inventory-transfer-foundation
strict result: vue-game-inventory-transfer-foundation
next safe stage: migrate-vue-game-stack-merge-foundation
source head: v377_auth_email_public_security
local/Neon DB current: v377_auth_email_public_security / v377_auth_email_public_security
v377 apply/stamp/downgrade: local 1/0/0; Neon 1/0/0
email rollout approval/execution: yes/public-live
public backend/static: v377/v378 Live
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
```

## 이번 체크포인트

- v399는 가방↔보관함 묶음 이동과 정렬 적용을 연결합니다. 순수 `transferItemSlot`이 source의 빈 칸·ID·강화·수량·추가 필드를 유지하고 destination 첫 빈 칸을 사용합니다. 자동 합치기는 아직 하지 않습니다.
- 전체 Vue smoke·TypeScript·production build PASS. 1366px/390px synthetic 브라우저에서 양방향 이동·정렬 저장·503 실패/재시도·pending 해제·가로 넘침 0·console error 0을 확인했고 임시 fixture는 제거했습니다.
- store는 prospective snapshot의 복구본 기록이 성공해야 화면을 바꾸고 공통 queue에 저장합니다. quota/다른 탭 변경은 변경 전 차단합니다. 저장 실패는 pending을 보존하며 재시도는 이동을 반복하지 않습니다. 저장 중/오류/전환 중 후속 변경을 잠그고 401/403은 로그인으로 돌아갑니다.
- 가방·보관함 정렬은 미리보기 후 `정렬 적용·저장`으로 확정합니다. 휴지통 정렬은 미리보기만 유지합니다. 장착·사용·판매·자동 합치기·휴지통 이동/복구/삭제·Gold·보상·난수는 연결하지 않았습니다.
- v398의 실제 보유 snapshot 표시·전체 칸·중복 선택·아이콘, v397의 계정/슬롯/캐릭터별 pending 복구 선택과 v396의 13px typography·좌우 창·공유 modal 접근성을 유지합니다.
- 실제 계정·DB·backend·env·secret·legacy·배포 변경은 없습니다. 브라우저 검증은 메모리 저장소와 가짜 API만 사용하며 Vue 서버만 npm ci 설치 후 재시작했습니다.
- 공개 backend v377/static v378만 Live이며 Vue v379~v399는 미배포입니다. legacy static 승인 SHA는 `c56525394a4099160e7a32e93dc2d3a0d54568b3`입니다. DB migration/메일/배포 상세 증거는 [현재 상태](docs/current/CURRENT_STATUS.md)를 따르고 재실행하지 않습니다.
- 관리자 Preview는 Bearer/isAdmin과 `dryRun: true`이며 Apply/재인증/dev key header는 잠겼습니다. production `admin` 승격/owner bootstrap도 별도 exact DB-write 승인 전까지 실행하지 않습니다.
- `saveVersion`은 형식 버전이며 backend CAS는 미구현입니다. 다중 탭 localStorage 비교도 원자적 CAS가 아닙니다. legacy 키 자동 가져오기/삭제·복구본 자동 정리/다운로드는 제공하지 않습니다.

## 바로 할 일

1. 다음은 `migrate-vue-game-stack-merge-foundation`입니다. legacy의 +0/스킬강화권 중첩 가능 여부와 template·tier·슬롯 비교 규칙을 순수 함수로 옮겨 가방↔보관함 이동 시 자동 합치기를 연결합니다. 수량 보존·가득 찬 목적지의 호환 묶음·강화 장비 비중첩·추가 옵션 보존을 검증합니다. 장착·사용·판매·휴지통 변경·Gold·난수·backend/CAS·DB write·배포는 분리합니다.
2. 실제 관리자 Apply API, 비밀번호 재인증 request, dev key header와 DB write는 연결하지 않습니다. 진행하려면 작업 종류와 exact DB-write 범위를 별도로 승인받습니다.
3. production 관리자 복구는 Vue 화면 이식과 분리하며 기존 `admin` 승격 또는 새 owner 생성의 exact DB-write 승인을 받기 전에는 실행하지 않습니다.

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
