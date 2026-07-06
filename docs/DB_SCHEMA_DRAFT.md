# PostgreSQL DB 설계 초안

이 문서는 현재 게임을 PostgreSQL로 옮기기 위한 1차 설계입니다.  
목표는 관리자 페이지에서 게임 수치를 바꿀 수 있게 하면서도, 유저 데이터가 꼬이지 않도록 분리하는 것입니다.

## 1. 설계 원칙

```txt
마스터 데이터 = 게임 원본 데이터
유저 데이터 = 유저가 실제로 가진 상태
관리자 변경 이력 = 누가 무엇을 어떻게 바꿨는지
```

예시:

```txt
item_templates = 심연의 편린 스태프라는 원본
item_instances = 특정 유저가 가진 +7 심연의 편린 스태프
```

## 2. 주요 테이블 그룹

### 계정/프로필

```txt
users
user_profiles
```

역할:

```txt
로그인 계정
골드
현재 캐릭터
현재 필드 진행도
기록/플래그 JSON
```

### 캐릭터/스킬

```txt
characters
skills
character_skills
skill_levels
user_character_skills
```

역할:

```txt
캐릭터 추가 대응
캐릭터별 스킬 연결
스킬 레벨별 수치
유저별 스킬 레벨/각성 상태
```

중요 원칙:

```txt
캐릭터마다 스킬만 다르고, 나머지 시스템은 공통 사용한다.
```

### 아이템/인벤토리/장비

```txt
item_templates
item_instances
user_inventory_slots
user_equipment_slots
```

역할:

```txt
아이템 원본
유저 보유 아이템
인벤토리/보관함/휴지통 슬롯
캐릭터별 장비 슬롯
```

### 보스/드랍

```txt
bosses
drop_tables
drop_table_items
```

역할:

```txt
일반 보스/특수 보스
보스별 드랍 테이블
드랍 아이템/확률/수량/조건
```

### 필드존

```txt
field_zones
```

역할:

```txt
필드명
몬스터 HP
골드 보상
입장 조건
공격력/공격속도 성장 규칙
```

### 강화

```txt
enhancement_groups
enhancement_levels
```

역할:

```txt
일반 장비 강화
심연의 편린 강화
탈리스만/휘장 강화
단계별 확률/비용/재료/증가 수치
```

### 우편/보상

```txt
user_mailbox_messages
```

역할:

```txt
관리자 보상 지급
이벤트 보상
시스템 보상
```

### 관리자/변경 이력

```txt
admin_roles
admin_user_roles
admin_change_logs
```

역할:

```txt
관리자 권한
수정 전/후 값
수정 사유
되돌리기 데이터
```

## 3. JSONB 사용 기준

PostgreSQL을 쓰되, 게임 옵션은 유연해야 하므로 일부 컬럼은 JSONB를 사용합니다.

JSONB 사용 추천:

```txt
아이템 특수 옵션
스킬 세부 옵션
보스 소환 조건
필드 성장 규칙
강화 재료 규칙
관리자 변경 전/후 데이터
```

일반 컬럼 사용 추천:

```txt
id
code
name
type
gold
level
rate
hp
created_at
updated_at
```

## 4. 관리자 페이지와 연결되는 핵심 테이블

```txt
아이템 관리      → item_templates
보스 관리        → bosses
드랍률 관리      → drop_tables, drop_table_items
필드존 관리      → field_zones
강화 규칙 관리   → enhancement_groups, enhancement_levels
캐릭터 관리      → characters
스킬 관리        → skills, character_skills, skill_levels
우편 지급        → user_mailbox_messages
변경 이력        → admin_change_logs
```

## 5. 다음 확정 작업

```txt
1. 현재 JS 데이터에서 item_templates seed 추출
2. bossList/specialBossList를 bosses + drop_tables로 변환
3. zones를 field_zones로 변환
4. skills.js를 characters/skills/character_skills/skill_levels로 변환
5. enhancement rules를 enhancement_groups/levels로 변환
6. Alembic 첫 마이그레이션 생성
```

세부 SQL 초안은 `backend/sql/schema_draft.sql`에 있습니다.


## v078 타입 보정

현재 게임의 보스 HP/필드 HP/골드 보상은 일반 `INTEGER` 범위를 넘는 값이 존재합니다.
따라서 아래 계열은 PostgreSQL에서 `NUMERIC(40,0)` 기준으로 설계합니다.

- `bosses.hp`
- `field_zones.enemy_hp`
- `field_zones.gold_reward`
- `enhancement_levels.gold_cost`
- `user_profiles.gold`

이 보정은 관리자 페이지에서 큰 수치를 직접 조정할 때도 필요합니다.
