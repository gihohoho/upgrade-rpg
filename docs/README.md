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
docs/current/POSTGRES_INITIAL_ALEMBIC_REVISION_CREATION.md
docs/current/POSTGRES_INITIAL_ALEMBIC_REVISION_MANUAL_REVIEW.md
docs/current/POSTGRES_MIGRATION_TEST_UPGRADE.md
```

## 인수인계

```txt
NEXT_CHAT_PROMPT.md
NEXT_CHAT_HANDOFF.md
docs/handoff/
```

루트 인수인계 파일과 `docs/handoff/` 사본은 같은 v298 기준으로 유지합니다.

## 폴더 역할

- `current/`: 현재 상태와 DB/Vue/FastAPI 전환 계획
- `contracts/`: 관리자 contract와 parity 기준
- `handoff/`: 다음 채팅 인수인계 사본
- `archive/`: 완료된 과거 단계 기록

`local-backups/`는 민감 DB 자료이고, `local-review-artifacts/`는 생성 revision 검토용 임시 bundle이므로 Git/전달 ZIP에서 제외합니다.
