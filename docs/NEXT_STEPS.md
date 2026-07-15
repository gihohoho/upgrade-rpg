# Next Steps — v306

## 지금 실행

```bash
python tools/check_postgres_next_revision_preflight.py --strict
```

## 결과 A — 후보 operation 0개

```txt
next-revision-not-required-current-schema-equivalent
```

- 새 revision을 만들지 않습니다.
- `v295_initial_schema` single baseline을 유지합니다.
- DB 구조 변경 요구가 생길 때까지 Alembic mutation 단계는 멈춥니다.

## 결과 B — 후보 operation 존재

```txt
next-revision-review-required-schema-differences-detected
```

- autogenerate를 실행하지 않습니다.
- table/column/index/FK/default/nullable별 의도를 먼저 검토합니다.
- 기존 748개 row 영향과 data migration 필요 여부를 문서화합니다.
- 별도 승인 후 isolated migration workspace 설계로 이동합니다.

## 계속 금지

- source/rehearsal stamp 재실행
- 새 revision/autogenerate
- source/rehearsal/migration upgrade/downgrade
- DB create/drop/restore
- `.env`, seed, 인증, API route/body/write 변경
- Docker volume 삭제
- 게임 콘텐츠/밸런스 변경
