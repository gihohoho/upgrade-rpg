# Documentation

## 현재 문서

새 채팅과 현재 작업에서는 먼저 아래를 확인합니다.

```txt
docs/current/README.md
docs/current/CURRENT_STATUS.md
docs/current/ROADMAP.md
docs/NEXT_STEPS.md
```

현재 PostgreSQL/Alembic 핵심 문서:

```txt
docs/current/POSTGRES_RUNTIME_READONLY_STATE.md
docs/current/POSTGRES_SCHEMA_EQUIVALENCE_CHECK.md
docs/current/POSTGRES_ALEMBIC_BASELINE_STRATEGY.md
docs/current/POSTGRES_BACKUP_RESTORE_PREP.md
docs/current/POSTGRES_BACKUP_CREATION.md
docs/current/POSTGRES_RESTORE_REHEARSAL_DB_CREATION.md
docs/current/POSTGRES_RESTORE_REHEARSAL.md
docs/current/POSTGRES_MIGRATION_TEST_DB_CREATION.md
```

## 인수인계

```txt
NEXT_CHAT_PROMPT.md
NEXT_CHAT_HANDOFF.md
docs/handoff/
```

루트 인수인계 파일과 `docs/handoff/` 사본은 같은 v294 기준으로 유지합니다.

## 문서 폴더

- `current/`: 현재 상태, DB 전환, Vue/FastAPI 전환, 로드맵
- `contracts/`: 관리자 contract와 parity 기준
- `handoff/`: 다음 채팅 인수인계 사본
- `archive/`: 완료된 과거 단계 기록
- 루트의 기능별 문서: 기존 smoke와 구현 이력이 참조하는 상세 기록

문서 대량 이동은 기존 smoke 경로를 확인한 뒤 진행합니다.

- `current/POSTGRES_RESTORE_REHEARSAL_DB_CREATION.md`: 빈 restore rehearsal DB 생성 안전 경계

- `current/POSTGRES_RESTORE_REHEARSAL.md`: verified dump isolated restore 및 사후 검증 경계

- `current/POSTGRES_MIGRATION_TEST_DB_CREATION.md`: 빈 Alembic migration test DB 생성 안전 경계
