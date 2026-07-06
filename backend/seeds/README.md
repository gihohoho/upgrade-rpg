# Backend Seeds

이 폴더는 현재 브라우저 JS 게임 데이터에서 추출한 PostgreSQL seed 초안을 보관합니다.

## 생성 방법

프로젝트 루트에서 실행합니다.

```bash
node tools/extract_seed_data.js
node tools/smoke_seed_extraction.js
```

## 생성 위치

```txt
backend/seeds/generated/
```

주요 파일:

```txt
characters.json
skills.json
skill_books.json
bosses.json
field_zones.json
item_templates.json
drop_tables.json
drop_table_items.json
enhancement_rules.json
manifest.json
```

## 주의

- 이 seed는 아직 DB에 자동 삽입하지 않습니다.
- 다음 단계에서 SQLAlchemy 모델/마이그레이션과 맞춰 seed import 스크립트로 발전시킬 예정입니다.
- 관리자 페이지에서 수정 가능해야 하는 데이터가 누락되지 않았는지 `docs/ADMIN_REQUIREMENTS_V1.md`와 함께 확인해야 합니다.
