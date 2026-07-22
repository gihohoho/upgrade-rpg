# Production deployment plan — v334

> v335에서 비용 최소 공급자는 Render Free Web Service Singapore + Neon Free PostgreSQL 16 Singapore로 선택했습니다. v336에서 Neon 프로젝트와 Direct/Pooler read-only TLS 연결을 검증했고, v337에서 Render `Hobby (legacy)`/no-card account와 Existing Image 흐름을 확인했습니다. Render registry credential/resource, 배포 secret, `rpg_game` DB/schema/data는 아직 준비되지 않았으므로 이 v334 실행 계획의 required input과 approval은 계속 닫혀 있습니다.

## 결론

운영 배포 계획 검토는 완료했습니다. 실제 배포 승인은 아직 열 수 없습니다. 검증된 image와 Compose 안전 경계는 준비됐지만 아래 운영 입력이 정해지지 않았기 때문입니다.

- 실제 production host/provider/region과 접속 방식
- managed PostgreSQL provider/product/region/endpoint와 private/public network 정책
- provider가 배포한 CA PEM과 host mount 경로
- reverse proxy 또는 managed ingress, domain, DNS, certificate 발급·갱신 책임
- 실제 secret을 Git 밖에서 주입할 위치
- proxy와 backend가 공유할 사전 생성 edge network 이름
- 첫 배포 장애 시 traffic 철회 담당과 managed DB backup 상태

정적 계약은 `deploy/production-deploy-plan.example.json`에 있습니다. 이 파일에는 실제 secret·endpoint·CA·domain 값을 넣지 않습니다.

## 승인 모델

이번 요청으로 승인된 것은 **계획 검토와 정리 작업**입니다. 실제 production resource 변경 승인은 아닙니다.

1. 위 입력을 모두 확정하고 실제 값은 승인된 secret/deployment platform에만 넣습니다.
2. Codex가 final Compose render, host preflight, rollback 절차를 포함한 실행 준비 commit을 만듭니다.
3. 기호가 그 commit의 정확한 40자리 SHA를 한 번 승인합니다.
4. 승인 범위 안에서만 GHCR login/pull, Compose 적용, read-only health, 기존 proxy route 확인을 실행합니다.
5. DB/Alembic mutation과 volume 삭제는 이 승인에 포함되지 않습니다.

개인 비공개 저장소의 GitHub environment에는 native required reviewer가 없고 현재 관리자 우회가 가능합니다. 따라서 source-controlled exact-SHA 승인을 계속 사용합니다.

## 고정 배포 대상

```txt
image: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2
platform: linux/amd64
backend replicas/workers: 1/1
database: managed PostgreSQL, provider CA verify-full
public entry: external reverse proxy HTTPS
host backend port: publish하지 않음
automatic migration/deploy: 사용하지 않음
```

이 image는 SBOM, Trivy HIGH/CRITICAL 0건, provenance, Cosign과 v333 isolated runtime 검증을 통과했습니다.

## 실행 순서

1. host architecture, Docker, disk, clock, outbound GHCR 연결을 읽기 전용 확인합니다.
2. secret 값을 출력하지 않고 필수 입력과 주입 경로가 모두 존재하는지 확인합니다.
3. exact digest와 signature evidence를 다시 확인합니다.
4. production host에서 승인된 credential 경로로 private GHCR에 로그인합니다.
5. exact digest만 pull하고 `RepoDigests`, `linux/amd64`를 확인합니다.
6. 기존 edge network와 provider CA 권한을 확인합니다.
7. sanitizing wrapper로 final Compose config를 render하고 placeholder·drift가 있으면 중단합니다.
8. host port, bundled DB, volume, migration 없이 backend 1개를 시작합니다.
9. `/api/v1/health`, UID 65532, read-only rootfs, resource limit, exact image를 확인합니다.
10. `verify-full`을 확인한 뒤 `/api/v1/health/db`를 읽기 전용 연결 검사로 한 번 확인합니다.
11. 기존 proxy route와 public HTTPS origin을 확인합니다.
12. secret 없는 배포 증거를 남기고 자동 배포는 계속 끕니다.

## 중단과 복구

- placeholder, digest 불일치, signature/scan 증거 불일치, CA hostname 검증 실패가 있으면 시작 전에 중단합니다.
- traffic 연결 전 실패하면 새 backend container만 제거합니다. DB, CA, network, volume은 건드리지 않습니다.
- traffic 연결 뒤 실패하면 proxy route를 철회하고 새 backend를 중지합니다.
- 첫 운영 배포라 이전 production image rollback target은 없습니다.
- DB schema/data를 바꾸지 않으므로 DB rollback은 수행하지 않습니다.
- 자동 재시도, `docker compose down -v`, Alembic 자동 실행은 금지합니다.

## 현재 상태

```txt
plan review: complete
approval ready: no
production deployment approved/executed: no/no
next safe stage: select-production-targets-and-complete-executable-deploy-plan
```
