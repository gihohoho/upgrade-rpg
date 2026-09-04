# Vue/FastAPI/DB 전체 전환 계획 — v394

## 현재 결론

`frontend/vue-app/`은 더 이상 단순 실험용 shell이 아니라 전체 프론트엔드를 옮길 작업공간입니다. 다만 공개 서비스의 `index.html`, `admin.html`, 루트 `src/`는 Vue 기능이 같은 수준으로 검증될 때까지 기준 구현으로 유지합니다.

v379에서 시작해 v394까지 완료한 기반:

- Vue 3 + Vite + Vue Router
- 새 Vue 코드의 TypeScript 적용
- Pinia 공통 상태 관리
- 반응형 sidebar, 공통 card, focus/skip-link 접근성
- 기존 FastAPI read-only API client와 관리자 GET 화면 유지
- typed auth/account API, Pinia account store, 로그인·이메일·8칸 캐릭터 gate
- typed admin access store, `/admin` route guard, Bearer 관리자 GET
- typed 관리자 dry-run Preview API/store와 diff·stale·차단 화면
- 최신 Preview SHA-256 재검증, exact 문구와 민감 입력 삭제를 포함한 write-locked 확인 modal
- legacy game state·systems·rules 의존성 보고서와 Vue 독립 typed domain
- 캐릭터 슬롯 요약과 기본 domain 상태를 구분해 표시하는 마을/HUD adapter·Pinia·반응형 UI
- PostgreSQL master-data 40개 필드, 기본 공격 계산과 action result를 사용하는 표시 전용 필드 전투 UI
- PostgreSQL master-data 보스, typed 드랍 규칙과 action result를 사용하는 표시 전용 보스 전투 UI
- PostgreSQL master-data 아이템, typed slot helper와 action result를 사용하는 표시 전용 인벤토리·장비 UI
- 보관함·휴지통의 빈 칸·첫 빈 칸·독립 수동 정렬과 파괴적 작업 잠금을 보여주는 표시 전용 UI
- 스킬 10단계와 강화 확률·비용·재료·결과 능력치, SQ·SW 첫 Lv.1 규칙을 보여주는 표시 전용 UI
- 구매 계약을 임의로 만들지 않는 item master-data 상점 카탈로그와 기존 전투 옵션의 임시 설정 미리보기 UI
- legacy형 데스크톱 내 정보/장비·가방/Gold 좌우 창, 접근 가능한 utility/mobile modal과 최소 12px 게임 가독성 계층
- server state·저장·보상·난수와 분리된 결정론적 client 기본 공격 runtime, 단일 timer와 pause/resume/cleanup lifecycle
- 선택 캐릭터 server snapshot GET, identity 재검증, typed normalize/apply, 빈 snapshot 기본 상태와 loading/retry/session-invalid UI
- legacy, backend, DB, 공개 배포 변경 없음

## TypeScript를 쓰는 이유

Vue 자체는 JavaScript만으로도 사용할 수 있습니다. 이 프로젝트에서는 계정, 8개 캐릭터 슬롯, 저장 snapshot, 전투 상태, 관리자 API처럼 서로 연결된 데이터가 많아서 TypeScript를 새 Vue 기반부터 적용합니다.

얻는 이점:

1. API 응답이나 저장 데이터의 필드 이름이 바뀌었을 때 실행 전에 오류를 찾습니다.
2. Pinia store와 Vue component가 주고받는 값의 형태를 명확히 고정합니다.
3. 수만 줄의 legacy 코드를 기능별로 옮길 때 누락된 호출과 잘못된 상태 접근을 줄입니다.
4. IDE 자동완성과 안전한 이름 변경을 사용할 수 있습니다.

전환 비용을 줄이기 위해 기존 legacy JavaScript 전체를 먼저 변환하지 않습니다. `allowJs`로 기존 JS API 모듈을 사용할 수 있게 두고, Vue로 실제 이식하는 파일부터 TypeScript로 바꿉니다.

## 설계 경계

| 영역 | 책임 | 원칙 |
|---|---|---|
| Vue component | 화면 렌더링, 사용자 입력 | 직접 DOM 조작 금지 |
| Pinia store | 화면과 세션 상태 | 서버 snapshot 계약을 바꾸지 않음 |
| domain module | 전투·아이템·스탯 계산 | Vue에 의존하지 않는 순수 로직 우선 |
| API client | FastAPI 통신 | 기존 route path와 response body 유지 |
| legacy | 현재 공개 게임의 기준 구현 | Vue 동등성 확인 전 삭제 금지 |

관리자 write, 실제 save, 인증 token 처리에는 기존 권한·충돌·보안 계약을 그대로 적용합니다. DB/env/secret/migration 변경은 각 단계의 별도 승인 없이는 실행하지 않습니다.

## 작업 순서

### 1. 공통 기반 — v379 완료

- TypeScript compiler와 `vue-tsc` 도입
- Pinia 등록 및 typed app store 생성
- Vue Router entry를 TypeScript로 전환
- 공통 layout/navigation/card 디자인 정리
- desktop/mobile과 keyboard focus 검증

### 2. 로그인·이메일·캐릭터 선택 — v380 완료

- 로그인, 가입, 이메일 인증·재전송
- 오류 코드별 사용자 메시지
- 계정별 캐릭터 슬롯 8개와 캐릭터 선택·생성
- 인증 전 게임 boot와 자동 저장 차단
- legacy와 같은 token·선택 캐릭터 key, session invalid와 network 오류 분기
- 생성·선택·이름 확인 삭제 modal, desktop/mobile 접근성 검증

### 3. 관리자 화면 — v383 확인 경계 준비 완료

- 기존 read-only 조회를 typed store 경계로 정리 — 완료
- 관리자 인증과 route guard — 완료
- 일반 사용자에게 관리자 UI를 렌더링하지 않음 — 완료
- side-effect 없는 Preview를 먼저 이식하고 diff·stale·차단 사유 표시 — 완료
- Preview → 최신 재검증 → exact 문구·본인 확인 modal — 완료
- 실제 재인증 request, dev key header, Apply와 DB write — 별도 exact 승인까지 잠금 유지

### 4. 게임 domain 분리 — v384 기반 완료

- `src/state`, `src/systems`, `src/rules`의 전역 의존성 목록화 — 완료
- 기본 state/save payload, slot, 공격·필드 상태, 보스 규칙, action result 계산을 Vue 독립 TypeScript module로 이전 — 완료
- 고정 입력에서 legacy와 동일한 출력 회귀 검증 — 완료
- 남은 전투·아이템 orchestration의 DOM·timer·난수 adapter 분리 — 각 게임 UI 단계에서 계속

상세 inventory는 [Vue Game Domain Dependencies](../../generated/VUE_GAME_DOMAIN_DEPENDENCIES.md)를 따릅니다.

### 5. 게임 UI — 진행 중

- 마을/HUD — v385 완료
- 필드 전투 UI 기반 — v386 완료
- 보스 전투 UI 기반 — v387 완료
- 인벤토리·장비 UI 기반 — v388 완료
- 보관함·휴지통 UI 기반 — v389 완료
- 스킬·강화 UI 기반 — v390 완료
- 상점·설정 UI 기반 — v391 완료
- legacy 게임 프레임·modal·가독성 복원 — v392 완료
- client 전투 runtime 기반 — v393 완료
- server snapshot read/load 기반 — v394 완료
- tooltip 통합과 세부 시각 조정

### 6. 저장과 runtime — 진행 중

- server snapshot load를 기준으로 연결 — v394 완료
- 자동·수동·전환 저장의 단일 직렬 queue — 다음
- `401/403`, network, `5xx`, revision conflict 분기
- timer 정지와 최종 저장 이후 캐릭터 전환

### 7. 병행 검증과 전환

- 같은 계정/캐릭터에서 legacy와 Vue 결과 비교
- 실제 브라우저와 focused smoke 검증
- 승인된 exact SHA만 공개 배포
- 안정화 후 Vue를 기본 진입점으로 바꾸고 legacy를 archive

## 로컬 실행

실행 위치: `frontend/vue-app`

Python `.venv`: 필요 없음

dependency 변경 시 설치:

```bash
npm ci
```

개발 서버:

```bash
npm run dev
```

주소:

```txt
http://127.0.0.1:5173/game
http://127.0.0.1:5173/admin
```

검증:

```bash
npm run typecheck
npm run build
```

프로젝트 루트의 focused smoke:

```bash
bash tools/run_smoke_vue_shell.sh
```

## 완료 기준

Vue 화면이 보이는 것만으로 전환 완료로 보지 않습니다. 로그인부터 캐릭터 선택, 게임 진행, 저장·복구, 관리자 권한까지 기존 계약과 회귀 검사를 통과하고 공개 배포 승인을 받은 시점에 기본 화면을 전환합니다.
