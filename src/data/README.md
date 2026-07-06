# src/data

게임 마스터 데이터 후보를 모아두는 폴더입니다.

## 현재 파일

```txt
skills.js          - 캐릭터/스킬/스킬강화권 마스터 데이터
bosses.js          - 보스/특수보스 원본 데이터
boss-factories.js  - 12티어 이상 고티어 보스/장비 생성 공식
boss-bootstrap.js  - 보스 데이터 후처리 실행 순서
zones.js           - 필드존 데이터
```

## 백엔드/DB 전환 기준

나중에 PostgreSQL로 옮길 가능성이 높은 데이터:

```txt
skills.js          → characters, skills, character_skills, skill_books
bosses.js          → bosses, special_bosses
boss-factories.js  → item_templates 생성 규칙 또는 seed 변환 스크립트
zones.js           → field_zones
```

