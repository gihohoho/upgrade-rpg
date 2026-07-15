# PostgreSQL next revision read-only plan — v306

## 현재 결론

v305에서 최초 baseline 완료 상태가 실제 통과했습니다. v306은 새 revision을 만들지 않고 Alembic metadata candidate diff가 존재하는지만 읽기 전용으로 확인합니다.

## v306 안전 순서

1. v305 completion state 재확인
2. Alembic graph single base/single head 확인
3. approved model source snapshot 확인
4. canonical SQLAlchemy/PostgreSQL schema differences=0 확인
5. PostgreSQL read-only transaction과 SQL write guard 활성화
6. Alembic `compare_metadata()`로 type/default/nullable/index/constraint 후보 수집
7. integer PK sequence ownership과 unowned sequence 확인
8. 후보 0개면 새 revision을 만들지 않음
9. 후보가 있으면 변경 의도 검토 단계에서 정지
10. autogenerate, revision 생성, upgrade/downgrade는 별도 승인

## v306에서 실행하지 않는 명령

```txt
python -m alembic revision --autogenerate
python -m alembic revision
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
createdb
dropdb
pg_restore
docker compose down -v
```

## 결과별 다음 경계

### 차이 0개

```txt
next-revision-not-required-current-schema-equivalent
```

현재 single baseline revision을 유지합니다. schema 변경 요구가 생기기 전까지 migration 작업을 멈춥니다.

### 후보 차이 있음

```txt
next-revision-review-required-schema-differences-detected
```

자동 생성하지 않습니다. 각 후보가 의도한 변경인지, 기존 748개 row에 어떤 영향을 주는지, schema migration과 data migration을 분리해야 하는지부터 검토합니다.
