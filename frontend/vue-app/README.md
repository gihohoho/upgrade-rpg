# Upgrade RPG Vue App — v391

이 폴더는 Upgrade RPG 전체 프론트엔드를 Vue로 옮기는 작업공간입니다. 현재 공개 게임과 관리자 화면은 아직 루트 `index.html`, `admin.html`, legacy `src/`를 사용합니다.

## 현재 범위

- Vue 3 + Vite + Vue Router
- 새 Vue 코드 TypeScript
- Pinia 공통·계정·관리자·게임 화면 상태
- 반응형 공통 layout과 접근성 기반
- `/game`: 로그인·가입·이메일 인증 안내, 계정별 캐릭터 슬롯 8개 gate, 선택 뒤 마을/HUD·필드·보스·인벤토리/장비·보관함/휴지통·스킬/강화·상점/설정 미리보기
- `src/game/domain`: Vue·DOM과 독립된 typed state·slot·전투 계산·규칙 기반
- `src/game/adapters/townHud.ts`: 캐릭터 슬롯 요약과 기본 domain 상태를 표시 전용 마을 view model로 변환
- `src/game/adapters/fieldCombat.ts`: PostgreSQL master-data 필드와 기본 domain 계산을 HP·보상·action 표시 모델로 변환
- `src/game/adapters/bossCombat.ts`: PostgreSQL master-data 보스와 typed 드랍 규칙을 HP·소환 조건·쿨타임·action 표시 모델로 변환
- `src/game/adapters/inventoryEquipment.ts`: master-data 아이템과 typed slot helper를 15개 장비·24개 가방 표시 모델로 변환
- `src/game/adapters/storageTrash.ts`: master-data 아이템과 typed slot helper를 각각 20개 보관함·휴지통 표시 모델로 변환
- `src/game/adapters/skillEnhancement.ts`: master-data 스킬·레벨과 강화 그룹·단계를 스킬 10단계·확률·비용·재료·결과 능력치 표시 모델로 변환
- `src/game/adapters/shopSettings.ts`: item master-data의 강화 기준 비용·판매 값과 기존 전투 옵션 기본값을 거래·runtime·저장 없는 상점/설정 표시 모델로 변환
- `/admin`: `isAdmin=true` route guard 뒤 read-only 조회, 생성·수정·되돌리기 dry-run Preview, 실제 쓰기 없는 Apply 확인 준비
- `/admin/access`: 관리자 로그인·권한 거부·network 재시도

`/game`은 typed API client와 Pinia account store로 인증 token과 선택 캐릭터를 처리합니다. 마을에서만 접속 캐릭터 바를 표시하고, 필드·보스·아이템·스킬/강화·상점/설정 화면은 기존 master-data와 기본 typed domain으로 표시 상태만 바꿉니다. 가방·보관함·휴지통 정렬은 빈 칸과 상대 순서 계약을, 스킬·강화는 SQ/SW 첫 Lv.1과 장비 강화 계약을 확인합니다. 상점은 구매 규칙을 만들지 않고 등록된 강화 기준 비용·판매 값만 보여 주며, 설정 토글은 별도 임시 state에만 반영합니다. 실제 snapshot load/save·장착·사용·판매·구매·강화·Gold/재료 소비·난수·이동·복구·영구 삭제·설정 저장·자동 저장·전투 runtime은 시작하지 않습니다. TypeScript 별칭은 폐기 예정인 `baseUrl` 없이 `paths`의 설정 파일 기준 상대 경로를 사용합니다. `/admin`은 관리자 권한 확인 전에는 렌더링하지 않으며 모든 GET/Preview에 Bearer를 사용합니다. Preview는 `dryRun: true`, Apply와 DB write는 잠금 상태입니다.

## 설치와 실행

실행 위치: `frontend/vue-app`

Python `.venv`: 필요 없음

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

```bash
npm run typecheck
npm run build
```

`npm run build`는 먼저 TypeScript 검사를 실행한 뒤 Vite production bundle을 만듭니다.
