# Upgrade RPG Codex handoff — v397

새 채팅은 루트 [AGENTS.md](AGENTS.md)를 먼저 읽고 이 문서를 이어서 사용합니다. 더 자세한 현재 상태는 [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)가 기준입니다.

```txt
latest: v397.vue-game-pending-unsynced-recovery-foundation
strict result: vue-game-pending-unsynced-recovery-foundation
next safe stage: migrate-vue-game-owned-item-snapshot-foundation
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
```

## 이번 체크포인트

- v397은 `upgradeRpgVueRecovery:v1:<userId>:<slotKey>:<accountCharacterId>`에 snapshot·pending·백업을 하나의 JSON으로 기록합니다. 실패·세션 만료·닫기에도 원본을 보존하며 재진입 시 local/server/취소를 직접 선택합니다. local은 공통 queue로 재전송, server는 기존 local을 `backups`에 보존, 취소는 기록 변화 없이 슬롯으로 돌아갑니다. 깨진 저장소는 fail-closed, 용량 부족은 명시적으로 알립니다.
- v397 전체 Vue smoke·TypeScript·build와 1366px/390px synthetic 브라우저 복구 선택·취소·키보드·배경 잠금 PASS. 테스트는 메모리 저장소/가짜 API를 사용했으며 실제 계정·DB write는 없습니다. 임시 fixture는 제거했습니다. npm ci 전에는 해당 Vue의 Vite/esbuild 파일 잠금을 확인해 설치 실패를 피합니다.
- 문서 구조·handoff·strict·report smoke·Python compileall PASS. 로컬본 재전송 실패는 ‘이 기기 복구본’으로 표시하고 서버 저장 완료로 오인시키지 않습니다. 이 마지막 표시 보강 뒤 recovery/town focused·build도 PASS했습니다.
- v396은 13px 이상 글자·명암 token과 desktop 공간을 정리하고 게임·계정 modal의 focus trap·배경 inert·Escape·초점 복귀를 공유합니다. 1200px 이상에서 좌우 정보/가방 창을 표시합니다. 관리자 helper 중복과 미사용 `gameReadOnlyApi.js`를 정리했으며 typed API와 공개 legacy는 유지합니다.
- v395의 60초 자동·수동·전환 저장 queue에 context generation을 추가했습니다. reset/reload 이전의 늦은 응답은 취소하고 409·401·403 뒤 대기/후속 POST를 차단합니다. 명시적 reload/reset 뒤 저장을 다시 허용하며 network/5xx는 재시도할 수 있습니다.
- 전체 Vue smoke·TypeScript·production build PASS. 1366px/390px synthetic 브라우저에서 마을·가방·캐릭터 modal, 키보드 순환/복귀·배경 잠금·409 후 재로드 PASS. 최종 저장 중 화면 이동도 잠급니다. 실제 DB write·backend·env·secret·legacy·배포는 변경하지 않았습니다. 중지된 Vue 서버만 시작했습니다.
- 현재 `saveVersion`은 snapshot 형식 버전이며 backend 다중 기기 CAS는 미구현입니다. 복구본 시각만으로 자동 선택하지 않으며 다른 탭의 변경이 감지되면 다시 확인합니다. legacy 키 자동 가져오기·삭제, DB·backend·배포 변경은 없습니다. Windows 설치 파일 잠금 때문에 중복 실행 중이던 Vue 서버 2개를 정리하고 1개로 다시 시작했습니다.
- 문서 구조·handoff·strict와 관련 report smoke PASS. AST import graph에서 남은 Vue 코드 66개 모두 entry에서 도달하며 미해결 import 0개입니다. 임시 브라우저 fixture는 제거했습니다. 공통 처리 이동 시 component의 옛 문자열에 묶인 smoke도 함께 옮겨 중간 검사 중단을 줄입니다.
- v379~v395의 TypeScript·Pinia·계정/8칸 캐릭터·typed game domain·마을/필드/보스/가방/장비/보관함/스킬/상점 UI·client 전투 timer·server load/save를 유지합니다. Gold/아이템 보상·난수·실제 아이템/스킬 변경·설정 영구 저장은 연결하지 않았습니다.
- 관리자 Vue는 `isAdmin=true` route guard와 Bearer GET, `dryRun: true` Preview 5종, SHA-256·exact 문구 재검증 modal까지 연결했습니다. 실제 Apply·재인증 request·dev key header는 잠겨 있습니다.
- 기호가 Docker와 로컬 로그인을 확인했습니다. 정상 실행 중인 서버를 재사용하며 반복 로그인 검사는 하지 않습니다.
- 공개 legacy v378은 SQ·SW 첫 Lv.1, 마을 전용 접속 캐릭터 바, 배포 관리자 전용 테스트 UI와 local/production API 주소 분리를 포함합니다. 승인 SHA `c56525394a4099160e7a32e93dc2d3a0d54568b3`에서 static deploy `dep-da5vn3m417fc738rs2bg`로 1회 배포됐습니다. Vue v379~v396은 배포하지 않았습니다.
- v377 이메일 인증·복구·삭제와 rate limit·body cap·semantic outbox·미인증 identity 회수는 공개 배포됐습니다. `email-validator==2.3.0`·`dnspython==2.8.0` Linux runtime/musllinux/dev lock과 local Brevo Naver 수신→링크 인증→로그인→8개 슬롯 E2E 증거를 보존합니다.
- local/Neon migration은 각각 1회 v377로 완료했습니다. stale 증거와 `recovery1` marker는 보존하며 최종 `recovery2` synthetic fixture 왕복·Neon fresh backup·apply 결과는 [현재 상태](docs/current/CURRENT_STATUS.md)에 통합합니다. reset·seed·restore·stamp·actual downgrade는 실행하지 않았습니다.
- Brevo Render outbound IP 허용과 outbox 성공 finalize 수정 뒤 공개 메일 전송을 확인했습니다. 현재 backend deploy는 `dep-da4tp7nqj5pc73b6l910`, production image는 `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:80e8f57618b2bd8bbac37fd63381e454434e06b67eff0cd8f4327796bdc1c677`입니다. 공개 health 200, Naver 테스트 주소 요청의 generic 202/no-store와 outbox 1회 sent 증거는 재실행하지 않습니다.
- production 로그인 계정 `admin`은 관리자 승격 전 상태이고 owner bootstrap은 실행하지 않았습니다. 실제 dev key·비밀번호·secret은 ignored 환경 파일에만 보존합니다. 상세 승인·배포·메일 이력은 [현재 상태](docs/current/CURRENT_STATUS.md)를 기준으로 합니다.

## 바로 할 일

1. 다음은 `migrate-vue-game-owned-item-snapshot-foundation`입니다. 현재 master-data 샘플인 가방·장비·보관함·휴지통을 선택 캐릭터의 실제 server state로 표시하되 빈 칸·등급·아이템 identity를 보존합니다. 장착/이동/사용/판매·Gold 소비·보상·난수는 동시에 연결하지 않습니다. CAS는 별도 backend 계약과 승인 범위입니다.
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
