# PostgreSQL next Alembic revision preflight — v306

> 현재 상태 — v371: 이 문서는 v306 당시 model/schema가 동일했던 읽기 전용 판정
> 기록입니다. 현재 local source graph head는 `v371_email_identity_lifecycle`,
> local/live/Neon DB current는 `v295_initial_schema`입니다. v371 revision source는
> 준비됐지만 실제 DB apply·downgrade·stamp는 0회입니다.

## 목적

최초 baseline 완료 후 새 migration을 관성적으로 만들지 않고, SQLAlchemy metadata와 실제 원본 PostgreSQL schema 사이에 **실제 후보 변경이 있는지 읽기 전용으로 판단**합니다.

## 도구

```txt
tools/check_postgres_next_revision_preflight.py
tools/smoke/backend/smoke_postgres_next_revision_preflight.py
```

실행 명령:

```bash
python tools/check_postgres_next_revision_preflight.py --strict
```

이 도구는 다음을 실행하지 않습니다.

```txt
alembic revision
alembic revision --autogenerate
alembic upgrade
alembic downgrade
alembic stamp
DB create/drop/restore
row write
.env 변경
```

## 읽기 전용 확인 범위

1. v305 baseline completion 상태와 v302/v304 실행 보고서 유지
2. 당시 Alembic graph가 `v295_initial_schema` 단일 base/single head인지 확인
3. 승인된 SQLAlchemy model 및 Alembic env 파일 13개의 SHA-256 snapshot 확인
4. 기존 canonical schema checker의 22/22 tables, differences=0 확인
5. Alembic `compare_metadata()` API를 PostgreSQL read-only transaction 안에서 실행
6. SQL statement guard로 `SELECT`, `WITH`, `SHOW`, `SET` 이외 SQL 차단
7. type, nullable, index, unique, FK, server default 후보 차이 수집
8. public sequence와 integer PK sequence ownership 비교
9. 후보 operation이 0개인지 판단

`compare_metadata()`는 revision 파일을 생성하지 않습니다. Alembic CLI의 `revision --autogenerate`도 호출하지 않습니다.

## 기대 결과 — 변경 없음

```txt
result: next-revision-not-required-current-schema-equivalent
next revision required: no
next safe stage: keep-single-baseline-no-new-revision
```

이 경우 v306 당시에는 새 revision을 생성하지 않았고 `v295_initial_schema` 단일 revision
상태를 유지했습니다. 이 결론은 이후 의도된 이메일 schema 변경을 담은 v371 source를
부정하지 않습니다.

## 후보 차이가 발견될 때

```txt
result: next-revision-review-required-schema-differences-detected
next revision required: yes
next safe stage: separate-schema-change-intent-review
```

이 결과는 revision 생성 승인이 아닙니다. table/column/index/FK/default/nullable별 후보를 검토해 변경 의도를 문서화한 뒤 별도 승인 경계로 이동합니다.

## 차단 조건

- source target이 `rpg_game`이 아님
- v305 baseline completion이 유지되지 않음
- Alembic multiple heads 또는 승인되지 않은 revision 존재
- model/env source snapshot 변경
- canonical schema differences 발생
- read-only transaction 또는 SQL write guard 비활성
- public sequence ownership 불일치 또는 unowned sequence 존재

## 다음 단계 원칙

- candidate operation 0개: 새 revision 생성 보류
- candidate operation 존재: 먼저 의도와 데이터 보존 영향을 검토
- autogenerate 실행은 별도 사용자 승인 필요
- 생성한다면 source가 아니라 isolated migration workspace에서 먼저 검토
- upgrade/downgrade 왕복과 source 적용은 각각 별도 승인

## v371 후속 원칙

- v371 의도 범위: `users` email/verification/`authVersion` 열 4개와
  `user_email_action_tokens` 1개 table
- source graph: v295 → v371 single head / source parity smoke PASS
- applied DB: 계속 v295
- dependency/lock 검토 → isolated migration review/roundtrip → exact apply SHA 승인 순서
- migration apply, Brevo 설정, owner bootstrap과 배포는 각각 별도 승인
