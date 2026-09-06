# Upgrade RPG Codex handoff — v396

새 채팅은 루트 [AGENTS.md](AGENTS.md)를 먼저 읽고 이 문서를 이어서 사용합니다. 더 자세한 현재 상태는 [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)가 기준입니다.

```txt
latest: v396.vue-frontend-refactor-readability-foundation
strict result: vue-frontend-refactor-readability-foundation
next safe stage: migrate-vue-game-pending-unsynced-recovery-foundation
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
```

## 이번 체크포인트

- v396은 13px 이상 글자·명암 token과 desktop 공간을 정리하고 게임·계정 modal의 focus trap·배경 inert·Escape·초점 복귀를 공유합니다. 1200px 이상에서 좌우 정보/가방 창을 표시합니다. 관리자 helper 중복과 미사용 `gameReadOnlyApi.js`를 정리했으며 typed API와 공개 legacy는 유지합니다.
- v395의 60초 자동·수동·전환 저장 queue에 context generation을 추가했습니다. reset/reload 이전의 늦은 응답은 취소하고 409·401·403 뒤 대기/후속 POST를 차단합니다. 명시적 reload/reset 뒤 저장을 다시 허용하며 network/5xx는 재시도할 수 있습니다.
- 전체 Vue smoke·TypeScript·production build PASS. 1366px/390px synthetic 브라우저에서 마을·가방·캐릭터 modal, 키보드 순환/복귀·배경 잠금·409 후 재로드 PASS. 최종 저장 중 화면 이동도 잠급니다. 실제 DB write·backend·env·secret·legacy·배포는 변경하지 않았습니다. 중지된 Vue 서버만 시작했습니다.
- 이번은 v395 기반 refactor이며 local fallback과 `pending-unsynced` 복구 구현은 없습니다. 현재 `saveVersion`은 snapshot 형식 버전으로, backend 다중 기기 CAS와 사용자 선택 복구는 다음 작업의 경계를 따릅니다.
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

1. 다음 Vue 전환 단계는 `migrate-vue-game-pending-unsynced-recovery-foundation`입니다. 저장 실패 때 계정·캐릭터별 local fallback과 `pending-unsynced` marker를 보존하고 재진입 시 local/server/취소를 사용자가 명시적으로 고르는 복구 gate를 이식하되 Gold/아이템 보상·난수 드랍과 자동 충돌 선택은 함께 연결하지 않습니다. 실제 다중 기기 CAS는 별도 backend 계약과 승인이 필요합니다.
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
