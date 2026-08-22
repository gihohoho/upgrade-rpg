# PostgreSQL 배포 migration 운영 원칙 — v377

## 목적

이 문서는 baseline 완료 이후 배포 환경에서 migration을 어떻게 다룰지 고정합니다.
현재 local DB는 `v377_auth_email_public_security`, Neon DB는 `v295_initial_schema`에 있습니다. v306의 “새 revision 불필요”는
당시 model/schema에 대한 역사이며 현재 source graph head는
`v377_auth_email_public_security`입니다. v371·v377은 local에 적용했고 Neon에는 적용하지 않았습니다.

## 핵심 원칙

- FastAPI **서버 시작 시 자동 migration을 실행하지 않습니다.**
- 앱 startup/lifespan에서 `upgrade`, `stamp`, `create_all`, reset을 호출하지 않습니다.
- migration은 앱 배포와 분리된 운영 작업으로 취급합니다.
- revision 생성, isolated 검증, 원본 DB 적용은 각각 **별도 승인**을 받습니다.
- 원본 DB 적용은 검증된 backup과 복구 절차가 준비된 뒤에만 검토합니다.
- 기존 source/rehearsal baseline `stamp`는 완료됐으므로 재실행하지 않습니다.

## migration 전 필수 경계

1. SQLAlchemy model/schema 변경 의도를 문서로 고정합니다.
2. v306과 같은 read-only comparison에서 후보 operation을 먼저 확인합니다.
3. migration 전 source DB backup을 만들고 SHA-256 및 TOC를 검증합니다.
4. 생성된 revision은 원본 DB가 아닌 isolated migration DB에서 먼저 검토합니다.
5. upgrade → downgrade → upgrade 왕복과 schema/data signature를 비교합니다.
6. 기존 API route path/response body, seed, 인증, write 의미에 미치는 영향을 따로 검토합니다.
7. 원본 DB 적용은 다시 별도 사용자 승인을 받습니다.

## 실행 분리

정상 서버 실행 명령에는 Alembic 명령을 묶지 않습니다.

```txt
금지 예시:
서버 시작 && alembic upgrade head
Docker entrypoint에서 자동 upgrade
FastAPI lifespan에서 alembic.command.upgrade 호출
```

v377 같은 실제 revision의 운영 migration은 전용 guard가 exact target DB, 현재
`v295_initial_schema`, exact target revision, source hash와 backup evidence를 확인한 뒤
별도 exact-SHA 승인을 받아 한 번만 실행하도록 설계합니다. `stamp head`로 v371·v377 schema
변경을 건너뛰지 않습니다.

## 장애 대응

- 실행 중 오류가 나면 자동 재시도하지 않습니다.
- 코드 rollback과 DB rollback을 분리합니다.
- 먼저 current revision과 schema/data signature를 읽기 전용으로 확인합니다.
- downgrade가 안전하다는 isolated 왕복 증거가 없는 경우 원본 DB에서 임의 downgrade하지 않습니다.
- backup restore는 별도 DB rehearsal을 통과한 절차만 사용합니다.
- `docker compose down -v`, `setup_dev_db.py --reset`, `dropdb`, `pg_restore`는 별도 명시 승인 없이는 실행하지 않습니다.

## 현재 v307 경계

- 새 revision 필요: 없음
- revision/autogenerate: 미승인
- upgrade/downgrade/stamp: 미승인
- `.env` 변경: 미승인
- Docker container/volume 변경: 미승인
- DB schema/data 변경: 없음

## 현재 v377 local 적용 경계

- local source graph head: `v377_auth_email_public_security`
- local/Neon DB current: `v377_auth_email_public_security` / `v295_initial_schema`
- private environment: 535개 ACL 비공개 고정, 서로 다른 email/abuse secret 4개 생성 완료
- `8db9bcb` isolated roundtrip: 성공했으나 canonicalization 수정 뒤 SHA-stale
- `8db9bcb` local backup: 751 rows 성공했으나 새 SHA에는 stale
- local apply: Alembic 전 fingerprint false mismatch safe-stop, report 없음, DB v295
- local attempt marker: 보존, 같은 action 수동·자동 재실행 금지
- `345872a` recovery1 isolated roundtrip·local backup·local exact apply: 각각 1회 성공
- local legacy 751 rows 보존, model 25 tables parity, local v377 확인
- Neon: untouched, backup/apply marker 없음
- apply/downgrade/stamp: local 1/0/0, Neon 0/0/0
- Brevo 설정, owner bootstrap, app deploy: migration 승인과 분리

기존 marker나 evidence를 삭제·덮어쓰거나 같은 action을 재실행하지 않습니다. 다음 단계는
Brevo local 실제 메일 검증이며, Neon은 별도 fresh backup과 exact 범위로만 진행합니다.

## v308 runtime hardening 이후에도 유지되는 원칙

`backend/Dockerfile`과 운영 Compose 초안이 추가됐지만 서버 command에는 Alembic 자동 migration을 넣지 않았습니다.
운영 revision 적용은 앞으로도 backup, isolated 왕복 검증, exact target/revision, 별도 승인을 요구합니다.
