# Upgrade RPG Codex handoff — v395

새 채팅은 루트 [AGENTS.md](AGENTS.md)를 먼저 읽고 이 문서를 이어서 사용합니다. 더 자세한 현재 상태는 [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)가 기준입니다.

```txt
latest: v395.vue-game-serialized-save-queue-foundation
strict result: vue-game-serialized-save-queue-foundation
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
```

## 이번 체크포인트

- v395는 선택 캐릭터의 typed server state를 호출 시점에 복제해 Bearer token, `character-N`, 32자리 `accountCharacterId`와 함께 `POST /api/v1/game/save`로 보냅니다. 요청 후 live state를 바꿔도 이미 대기 중인 payload가 바뀌지 않으며 응답 type·data·payload identity와 saveVersion을 다시 검증합니다.
- 60초 자동 저장, 마을 수동 저장, 캐릭터 변경·로그아웃 전 최종 저장은 실패 뒤에도 다음 요청을 처리할 수 있는 하나의 Promise 직렬 queue를 공유합니다. 전환은 runtime pause → 앞선 queue와 최종 저장 대기 → 성공 뒤 selection/token 정리 순서이며 실패하면 전환을 막고 현재 context를 유지합니다.
- 401/403은 session invalid, 409는 자동 덮어쓰기와 후속 자동 저장을 멈추는 conflict, network/timeout/429/5xx는 token·선택을 보존하는 retryable 오류, 413/422와 응답 불일치는 contract 오류입니다. `saveVersion`은 기존 snapshot 형식 버전일 뿐 CAS revision이 아니므로 `expectedRevision`을 만들지 않았고 backend CAS는 여전히 공개 전 blocker입니다.
- focused queue/adapter/Pinia store/UI smoke, 전체 Vue shell smoke, TypeScript 검사와 production build가 PASS했습니다. 실제 DB save POST는 실행하지 않았고 backend·DB·env·secret·legacy·Render는 변경하지 않았으며 v395 production 승인/실행은 없습니다. Chrome·확장·native host는 설치 정상이지만 이번 제어 연결이 끊겨 mock fixture 브라우저 조작은 완료하지 못했고 fixture는 제거했습니다.
- v394의 server snapshot load, 신규 빈 상태, retry/session 분기와 v392의 desktop 좌우 창·mobile modal·최소 12px 가독성은 그대로 유지합니다.
- v384~v390의 typed domain·마을/HUD·필드·보스·인벤토리/장비·보관함/휴지통·스킬/강화 UI와 `baseUrl` 제거 상태를 유지합니다. 관리자 Apply route/header/write도 계속 없습니다.
- v381~v383 관리자 Vue는 `isAdmin=true` route guard, Bearer GET, `dryRun: true` Preview 5종과 SHA-256·exact 문구 재검증 modal까지 이식했습니다. 비밀번호·dev key는 저장·전송하지 않고 Apply route/header/write와 최종 버튼은 잠겨 있습니다.
- 기호가 Docker·로컬 로그인 정상 동작을 확인했습니다. Vue dev server는 `127.0.0.1:5173`에서 실행 중이며 반복 로그인 검사는 하지 않습니다.
- 기존 공개 legacy·backend·DB·env·secret·Render는 변경하지 않았고 Vue v382~v395 production 승인/실행은 없습니다.
- 특Q(SQ)·특W(SW)는 첫 전용 강화권 사용 뒤 저장·표시·전투 유효 레벨이 모두 1이며, 탈리스만 A/B의 일반 스킬 보너스를 더 이상 상속하지 않습니다. 기존 R·T와 F·D 보너스는 유지하고 source/generated skill metadata와 탈리스만 설명도 같은 계약으로 맞췄습니다.
- 상단 `접속 캐릭터` 바는 계정·캐릭터가 있고 현재 구역이 `town`일 때만 표시합니다. 초기 상태와 동기화 실패도 hidden/inert로 닫힙니다.
- 로컬에서는 기존 테스트 편의를 유지하지만 배포 origin에서는 로그인 사용자의 `isAdmin=true`일 때만 테스트 패널·테스트 지급 모달·MASTER DATA/SAVE DATA 개발 배지를 표시합니다. 이는 화면 노출 계약이며 client-authoritative save의 근본 치트 방지는 향후 server save 검증/CAS 범위입니다.
- 로컬 화면은 과거 localStorage에 남은 production URL이나 `127.0.0.1:8001` 같은 stale 포트를 무시하고 `http://127.0.0.1:8000/api/v1`로 고정합니다. 배포 화면은 Render API로 고정하며 관리자 페이지의 `기본값` 복원도 현재 환경 주소를 사용합니다.
- 실제 Chrome에서 stale `8001`로 향하던 `Failed to fetch`를 재현한 뒤 수정본이 로컬 API의 정상 인증 오류 응답까지 도달함을 확인했습니다. backend/static 서버 재시작은 필요하지 않습니다.
- local과 Neon 모두 `local-dev` legacy row만 `is_admin=true`이지만 password가 없고 이메일 미인증이라 로그인 가능한 관리자가 아닙니다. production의 로그인 가능 계정 `admin`은 현재 `is_admin=false`입니다. dev key는 두 ignored dotenv에 존재하지만 값은 Git·문서·채팅에 기록하지 않습니다.
- 승인 SHA `c56525394a4099160e7a32e93dc2d3a0d54568b3`의 legacy static을 Render deploy `dep-da5vn3m417fc738rs2bg`로 정확히 1회 배포했습니다. build는 298개 파일, secret 포함 없음으로 끝났고 public index/admin·v378 핵심 자산이 HTTP 200이며 미로그인 배포 화면에서 테스트 패널이 denied/hidden임을 확인했습니다. backend·DB·secret은 변경하지 않았고 자동 재시도도 없었습니다.
- v371 이메일 인증·복구·삭제와 v377 rate limit, JSON 파싱 전 body cap, semantic outbox, 미인증 identity 회수, 202·429·413 frontend 계약이 공개 서비스에 배포됐습니다.
- private environment와 ACL 준비, `email-validator==2.3.0`·`dnspython==2.8.0` Linux runtime/musllinux/dev lock, local Brevo 실제 Naver 메일→링크 인증→로그인→캐릭터 슬롯 8개 E2E는 완료 증거로 보존합니다.
- stale `8db9bcb`와 `recovery1` marker/evidence는 삭제·덮어쓰기하지 않았습니다. 최종 `recovery2` synthetic fixture의 `v295 → v377 → v295 → v377`을 1회 통과한 뒤 untouched Neon의 fresh custom backup과 v295→v377 apply를 각각 1회 완료했습니다.
- Neon apply는 기존 22개 table을 `SHARE ROW EXCLUSIVE`로 잠근 단일 transaction에서 수행했습니다. legacy 748 rows 변화 0, 25개 model table parity, 최종 revision `v377_auth_email_public_security`을 확인했습니다.
- DB reset·seed·restore·stamp·actual downgrade와 자동 retry는 실행하지 않았습니다. 운영 rollback은 additive v377 DB를 유지하고 이전 image로만 수행합니다.
- GitHub Actions run `32576889295`의 `run_attempt=1`이 linux/amd64 image를 게시·서명·검증했습니다. production image는 `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:a91d020c6b8abfbbcca56c1ff3ff7736c155fd43d854398e42bb0e42450ec994`입니다.
- Render 기존 backend service에는 email/security 환경변수 35개를 값 노출 없이 저장했습니다. backend deploy `dep-da4qqi3tqb8s738l68h0`은 새 exact digest로 live이며 자동 retry는 없었습니다.
- legacy static deploy `dep-da4qr867bikc73aekck0`은 commit `ceea14c20ac8604d453930d8f6c5127f00236352`에서 1회 build되어 live입니다.
- 공개 backend health는 HTTP 200입니다. auth malformed/schema 요청은 422와 `Cache-Control: no-store`, 허용된 Naver 테스트 주소의 인증메일 재요청은 generic 202 accepted와 `no-store`를 반환해 이전 `auth_protection_unavailable`·이메일 보안 미준비 503이 사라졌습니다.
- 첫 production 메일 미도착의 원인은 Brevo가 Render shared outbound IP를 차단한 것이었습니다. Render가 표시한 공식 CIDR `74.220.52.0/24`, `74.220.60.0/24`를 Brevo Authorized IP에 등록한 뒤 인증 메일이 provider에서 Delivered로 확인됐습니다.
- 그 메일은 실제 전송됐지만 outbox 성공 마감 중 `completed_at`보다 먼저 `sent` 상태가 autoflush되어 CHECK 제약에 걸렸습니다. `de3ae5d`에서 성공 상태 필드 설정 순서를 고쳤고 회귀 검사를 추가했습니다.
- 승인된 preparation `cd357de032425138d44323dd3060bbbf5b6a45d8`에서 authorization `46c9e7e33d866b160b6f4a8f36d5b68dabe3ece4`, immediate closure `e07474d5b5411dd805736687d1003f451298dae4`, evidence record `3e3516299a72e47c6d85597f8c0b60db5cb11a46`를 push했습니다. GitHub Actions run `32587614153`의 최초 1회가 signed digest `sha256:80e8f57618b2bd8bbac37fd63381e454434e06b67eff0cd8f4327796bdc1c677`를 게시했고 Render backend deploy `dep-da4tp7nqj5pc73b6l910`이 live입니다.
- 배포 뒤 공개 비밀번호 재설정 요청은 202와 `no-store`였고, Neon의 최신 outbox와 token은 1회 시도로 `sent`, provider 기록 존재, 오류 없음으로 마감됐습니다. 이미 인증된 테스트 계정의 인증메일 재전송은 의도대로 suppressed됐습니다.
- 공개 index는 로그인·회원가입·아이디 찾기·비밀번호 재설정·인증메일 재요청 UI를 표시하고, admin은 미로그인 상태에서 관리자 계정 확인 gate를 표시합니다.
- owner bootstrap은 별도 one-shot이며 실행하지 않았습니다.

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
