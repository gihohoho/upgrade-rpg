# JS 마스터 데이터 Seed 추출

## 목적

현재 게임의 마스터 데이터는 아직 브라우저 JavaScript 파일에 있습니다.

```txt
src/data/bosses.js
src/data/zones.js
src/data/skills.js
src/systems/stat-system.js
```

백엔드/PostgreSQL로 이전하려면 이 데이터를 사람이 손으로 옮기지 않고, 먼저 JSON seed 초안으로 추출해야 합니다.

## 실행 명령어

프로젝트 루트에서 실행합니다.

```bash
node tools/extract_seed_data.js
node tools/smoke/game/smoke_seed_extraction.js
```

## 출력 파일

```txt
backend/seeds/generated/characters.json
backend/seeds/generated/skills.json
backend/seeds/generated/skill_books.json
backend/seeds/generated/bosses.json
backend/seeds/generated/field_zones.json
backend/seeds/generated/item_templates.json
backend/seeds/generated/drop_tables.json
backend/seeds/generated/drop_table_items.json
backend/seeds/generated/enhancement_rules.json
backend/seeds/generated/manifest.json
```

## 현재 추출 기준

```txt
characters: 캐릭터 마스터 데이터
skills: 스킬 마스터 데이터
skill_books: 스킬강화권 매핑
bosses: 일반/특수 보스 마스터 데이터
field_zones: 필드존 마스터 데이터
item_templates: 드랍 아이템 원본 후보
drop_tables: 보스별 드랍 테이블 후보
drop_table_items: 보스별 드랍 아이템/확률 후보
enhancement_rules: 일반 장비 강화 테이블/확률 초안
```

## 아직 DB에 바로 넣지 않는 이유

현재 seed는 PostgreSQL 테이블에 넣기 전 단계입니다. 다음 작업에서 아래를 추가해야 합니다.

```txt
1. SQLAlchemy 모델과 seed JSON 필드 매칭
2. Alembic 마이그레이션 적용
3. seed import 스크립트 작성
4. /game/master-data API에서 DB 값을 읽도록 연결
```

## 관리자 페이지 요구사항과의 관계

관리자 페이지에서 수정해야 하는 값은 seed와 DB에 반드시 존재해야 합니다.

예:

```txt
보스 HP
드랍률
아이템 옵션
스킬 계수
강화 확률
필드 보상
캐릭터별 스킬 구성
```

관련 문서:

```txt
docs/archive/stage-notes/ADMIN_REQUIREMENTS_V1.md
docs/archive/stage-notes/DB_SCHEMA_DRAFT.md
docs/archive/stage-notes/BACKEND_API_ROUTES_DRAFT.md
```
