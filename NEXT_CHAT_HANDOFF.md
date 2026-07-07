# Upgrade RPG — Next Chat Handoff

이 문서는 새 채팅에서 바로 이어가기 위한 인수인계 문서입니다.

## 사용자/응답 방식

- 이 프로젝트에서 질문하는 사람은 **기호**입니다.
- 기호는 코딩/터미널/경로에 익숙하지 않습니다.
- 명령어를 줄 때는 항상 먼저 실행 위치를 적어야 합니다.

예:

```txt
위치: 프로젝트 루트
위치: backend 폴더 + 가상환경 activate 상태
위치: 브라우저 개발자도구 Console
```

## 프로젝트 기본 정보

- 현재 프로젝트는 아직 Vue가 아니라 **index.html + JS + CSS 기반 RPG 게임**입니다.
- 장기 목표는 **Vue 프론트엔드 + FastAPI 백엔드 + PostgreSQL + 관리자 페이지** 구조입니다.
- 지금은 기존 게임이 완전히 정상 작동하는 상태를 유지하면서 단계적으로 백엔드를 붙이고 있습니다.

GitHub repo:

```txt
https://github.com/gihohoho/upgrade-rpg.git
```

로컬 경로:

```txt
프로젝트 루트: ~/Desktop/Upgrade RPG
backend 폴더: ~/Desktop/Upgrade RPG/backend
```

백엔드 실행:

```bash
# 위치: backend 폴더 + 가상환경 activate 상태
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

PostgreSQL/Docker:

```txt
DB 컨테이너: upgrade_rpg_postgres
Adminer 컨테이너: upgrade_rpg_adminer
PostgreSQL host port: 55432
Adminer: 8081
DATABASE_URL:
postgresql+asyncpg://rpg_user:rpg_password@127.0.0.1:55432/rpg_game
```

localStorage save key:

```txt
idleRpgSaveV22
```

관리자 쓰기 dev key:

```txt
local-admin-dev-key
```

## 현재 안정 버전

- 최신 안정 버전: **v138: admin safe apply review**
- 최신 ZIP 이름: **rpg_v138_admin_safe_apply_review.zip**

v138은 관리자 마스터 데이터 편집에서 적용 직전 before/after 비교 UI를 추가하고, high risk 변경에는 `HIGH RISK EDIT` 추가 확인 문구를 요구하는 버전입니다. v135의 카탈로그 페이지네이션, 기본 20개 표시, ID순 정렬, 인게임 슬롯 이름 표시도 유지합니다.
DB schema, seed 데이터, localStorage 저장 구조는 변경하지 않았습니다.
DB reset/seed는 필요 없습니다.

## 현재까지 완료된 핵심 기능

### master-data 연결

- PostgreSQL → FastAPI → 브라우저 master-data 연결 완료.
- 기본 mode는 `auto`.
- 백엔드 master-data 실패 시 기존 static JS 데이터로 fallback.
- MASTER DATA dev badge 유지.

### save-data 연결

- 기존 localStorage 저장 유지.
- 수동 저장 시 DB save snapshot에도 저장하는 dual write 완료.
- SAVE DATA dev badge 유지.
- DB 세이브/localStorage 비교 preview 완료.
- DB 세이브 복구 안전장치 완료.
- 복구 전 localStorage 자동 백업 완료.
- 복구/백업 되돌리기 후 reload lock으로 beforeunload 자동저장 덮어쓰기 방지 완료.
- DB save slot 목록 조회 완료.
- save-data integrity verify 완료.

### 관리자 페이지

- `admin.html` 분리 완료.
- 관리자 overview, 세이브 스냅샷 필터, 마스터 데이터 카탈로그, 상세, 관계 보기 완료.
- 관리자 편집 초안 UI 완료.
- 초안 검증 dry-run 완료.
- 일부 allow-list 필드 실제 DB 적용 완료.
- 관리자 변경 이력 저장 완료.
- 변경 이력 상세 보기 및 rollback 완료.
- 변경 이력 필터 완료.
- write dev key guard 완료.
- edit stale guard 완료.
- master-data API 반영 확인 및 post-edit 자동 확인 완료.
- v133에서 편집 초안 입력 UI 타입 개선 완료.
  - boolean 필드: true/false select
  - number 필드: number input
  - description/admin_note: textarea
  - 읽기 전용/잠금 필드 카드 표시
- v134에서 admin safe selects + allow-list 확장 완료.
- v135에서 마스터 데이터 카탈로그 페이지네이션 + 슬롯 이름 표시 완료.
  - itemTemplates.item_type 실제 적용 가능
  - itemTemplates.equip_slot 실제 적용 가능
  - skills.slot_key 실제 적용 가능
  - item_type/equip_slot/boss_type/slot_key preset select
  - risk high/medium/low 배지
- v138에서 관리자 적용 직전 비교 UI + high risk 추가 확인 완료.
  - 변경된 필드만 before/after 표시
  - 위험도 순 정렬
  - high risk 변경 시 HIGH RISK EDIT 추가 입력 필요
  - 카탈로그 현재 선택 행 강조

### runtime 반영

- 관리자에서 보스 hp 수정 후 게임 새로고침 시 인게임 보스 체력 반영 확인 완료.
- `itemTemplates.stackable` 값이 신규 획득 아이템 겹치기에 연결 완료.
- 겹친 stackable 장비 강화 시 1개 분리 처리.
- 겹친 장비 강화 시 가방/보관함이 꽉 차 있으면 강화 차단 완료.

## 중요한 안전 규칙

- 기존 게임 동작을 깨면 안 됩니다.
- localStorage 저장은 계속 유지해야 합니다.
- DB 저장은 기존 localStorage 저장을 대체하지 않고 보조/동기화 구조로 유지합니다.
- 기존 세이브에 이미 따로 들어간 stackable 아이템을 자동 병합하지 않습니다.
- 관리자 쓰기 API는 dev key + 확인 문구 + stale guard를 유지해야 합니다.
- 새 기능을 만들 때 DB reset/seed 필요 여부를 반드시 알려줘야 합니다.
- `.env`, `.gitignore`는 변경될 때만 zip에 포함하면 됩니다.

## 현재 관리자 쓰기 흐름

실제 적용:

```txt
관리자 페이지 → 마스터 데이터 카탈로그 → 보기
→ 관리자 편집 초안 수정
→ 초안 검증
→ dev key 저장 상태 확인
→ 확인 문구 입력: APPLY MASTER DATA EDIT
→ high risk 변경이 있으면 추가 확인 문구 입력: HIGH RISK EDIT
→ 검증 후 실제 적용
→ 변경 이력 저장
→ master-data API 자동 반영 확인
→ 게임 새로고침 후 인게임 반영
```

되돌리기:

```txt
관리자 변경 이력 → 보기
→ 되돌리기 미리보기
→ 확인 문구 입력: ROLLBACK MASTER DATA EDIT
→ 검사 후 되돌리기
→ 변경 이력 저장
→ master-data API 자동 반영 확인
→ 게임 새로고침 후 인게임 반영
```

## 현재 주요 확인 명령어

```bash
# 위치: 프로젝트 루트
bash tools/run_smoke_core.sh
```

```bash
# 위치: 프로젝트 루트
bash tools/run_smoke_all.sh
```

```bash
# 위치: backend 폴더 + 가상환경 activate 상태
python scripts/check_admin_readonly_api.py
```

브라우저 확인:

```js
// 위치: 브라우저 개발자도구 Console
checkAdminReadOnlyPageReady();
```

```js
// 위치: 브라우저 개발자도구 Console
getAdminDraftFieldInputKind({ key: "stackable", value: true });
```

## 다음 단계 추천

가장 안전한 다음 단계 후보:

1. **관리자 변경 전후 비교 UI 강화**
   - 실제 적용 전에 “바뀌는 필드만” 더 눈에 잘 보이게 표시.
   - 위험도 높은 변경은 상단에 한 번 더 강조.
   - item_type / equip_slot / slot_key 변경 시 별도 경고 문구 표시.

2. **관리자 allow-list 추가 확장 검토**
   - dropTables.owner_type, skillLevels.level, enhancementLevels.from_level 같은 관계성 필드는 조심스럽게 검토.
   - 관계 필드(`*_id`, `*_code`)와 JSON 필드는 아직 잠금 유지.

3. **정식 인증/권한 설계 준비**
   - 현재 dev key는 로컬 개발용 안전장치일 뿐입니다.
