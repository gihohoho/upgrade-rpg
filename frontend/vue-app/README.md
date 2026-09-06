# Upgrade RPG Vue App — v396

이 폴더는 Upgrade RPG 전체 프론트엔드를 Vue로 옮기는 작업공간입니다. 현재 공개 게임과 관리자 화면은 아직 루트 `index.html`, `admin.html`, legacy `src/`를 사용합니다.

## 현재 범위

- Vue 3 + Vite + Vue Router
- 새 Vue 코드 TypeScript
- Pinia 공통·계정·관리자·게임 화면 상태
- 반응형 공통 layout과 접근성 기반
- `/game`: 로그인·가입·이메일 인증 안내, 계정별 캐릭터 슬롯 8개 gate, 선택 뒤 마을/HUD·필드·보스와 legacy형 내 정보/장비·가방 side window, 인벤토리/장비·보관함/휴지통·스킬/강화·상점/설정 modal 미리보기
- `src/game/domain`: Vue·DOM과 독립된 typed state·slot·전투 계산·규칙 기반
- `src/game/runtime/combatRuntime.ts`: 필드·보스의 결정론적 기본 공격, 단일 timer와 일시정지·재개·정리 lifecycle을 담당하는 client-only runtime
- `src/game/adapters/townHud.ts`: 캐릭터 슬롯 요약과 기본 domain 상태를 표시 전용 마을 view model로 변환
- `src/game/adapters/fieldCombat.ts`: PostgreSQL master-data 필드와 기본 domain 계산을 HP·보상·action 표시 모델로 변환
- `src/game/adapters/bossCombat.ts`: PostgreSQL master-data 보스와 typed 드랍 규칙을 HP·소환 조건·쿨타임·action 표시 모델로 변환
- `src/game/adapters/inventoryEquipment.ts`: master-data 아이템과 typed slot helper를 15개 장비·24개 가방 표시 모델로 변환
- `src/game/adapters/storageTrash.ts`: master-data 아이템과 typed slot helper를 각각 20개 보관함·휴지통 표시 모델로 변환
- `src/game/adapters/skillEnhancement.ts`: master-data 스킬·레벨과 강화 그룹·단계를 스킬 10단계·확률·비용·재료·결과 능력치 표시 모델로 변환
- `src/game/adapters/shopSettings.ts`: item master-data의 강화 기준 비용·판매 값과 기존 전투 옵션 기본값을 거래·runtime·저장 없는 상점/설정 표시 모델로 변환
- `/admin`: `isAdmin=true` route guard 뒤 read-only 조회, 생성·수정·되돌리기 dry-run Preview, 실제 쓰기 없는 Apply 확인 준비
- `/admin/access`: 관리자 로그인·권한 거부·network 재시도

`/game`은 선택 캐릭터의 서버 snapshot을 읽은 뒤 시작하며 자동·수동·전환 저장을 하나의 직렬 queue로 보냅니다. 401/403·409 뒤 후속 저장을 차단하고 이전 context의 늦은 응답은 취소합니다. 충돌 시 사용자가 명시적으로 서버 상태를 다시 불러올 수 있으며 local fallback·pending-unsynced·backend CAS는 다음 단계입니다.

1200px 이상에서는 내 정보/장비·가방/Gold를 게임 양옆에 유지하고, 좁은 화면에서는 하단 버튼과 모바일 modal을 사용합니다. 게임·계정 modal의 Tab 순환·Escape·배경 잠금·초점 복귀는 공통 composable이 맡습니다. 보조 글자는 13px 이상 token을 사용합니다. 마을에서만 접속 캐릭터 바가 표시됩니다.

전투 timer와 client HP는 저장할 server state와 분리합니다. 아이템/스킬 변경·Gold/재료 소비·보상·난수·설정 영구 저장은 아직 연결하지 않았습니다. 자세한 기능 경계는 [Vue 전환 계획](../../docs/reference/frontend/VUE_FASTAPI_DB_TRANSITION_PLAN.md)을 따릅니다. TypeScript는 `baseUrl` 없이 상대 `paths`를 사용합니다. 관리자 GET/Preview는 Bearer와 권한 gate를 유지하며 실제 Apply는 잠겨 있습니다.

## 설치와 실행

실행 위치: `frontend/vue-app`

Python `.venv`: 필요 없음

새 설치: `npm ci`가 lockfile 기준으로 의존성을 설치합니다. Windows PowerShell에서 실행 정책에 막히면 `npm.cmd`를 사용합니다.

```bash
npm ci
npm run dev
```

확인 주소:

```txt
http://127.0.0.1:5173/game
http://127.0.0.1:5173/admin
```

## 검사와 빌드

실행 위치: `frontend/vue-app` · Python `.venv`: 필요 없음 · 새 설치: 위 설치 완료 시 없음

```bash
npm run typecheck
npm run build
```

`npm run build`는 먼저 TypeScript 검사를 실행한 뒤 Vite production bundle을 만듭니다.
