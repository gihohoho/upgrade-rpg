# Production secret / TLS / container static validation — current through v321

현재 backend production reference는 `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2`로 정적 고정되어 있습니다. 이 값은 아직 pull·container·deploy에 적용하지 않았습니다.

## 현재 정적 계약

- production Compose service: backend only
- bundled PostgreSQL/Adminer/host ports/build/named volumes: absent
- managed PostgreSQL TLS: `verify-full` + provider CA
- external reverse proxy edge network
- backend replicas/workers: 1/1
- backend image reference: registry/namespace/repository + exact SHA-256 digest
- backend filesystem: read-only, `/tmp` tmpfs, no-new-privileges
- Dockerfile: non-root, Alembic 자동 실행 없음

기호 PC의 config render-only는 이미 통과했습니다. 이 문서의 checker는 계속 repository 파일만 읽으며 Docker, DB, Alembic을 실행하지 않습니다.

## 현재 승인 상태

```txt
config render approved/executed: yes/yes
image pull/build/push approved: no/no/no
container execution approved: no
actual production values applied: no
```

## 읽기 전용 검사

```bash
python tools/check_production_secrets_tls_container_static.py --strict
```

정상 결과의 다음 단계:

```txt
next safe stage: select-registry-repository-platform-and-base-image-digest
```
