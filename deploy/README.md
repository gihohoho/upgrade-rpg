# Production deployment — v336

이 폴더는 운영 배포의 source-controlled template과 sanitized evidence를 보관합니다. 실제 secret·CA·certificate·private key는 넣지 않습니다.

## 현재 준비된 것

- `docker-compose.production.yml`: managed PostgreSQL과 외부 reverse proxy를 사용하는 backend 1개
- `production.env.example`: verified exact digest와 필수 변수 inventory
- `production-deploy-plan.example.json`: 검토된 실행 순서·승인·rollback 계약
- `production-provider-selection.example.json`: Render Free + Neon Free 비용 최소 선택과 미해결 onboarding 계약
- `backend-image-ghcr-policy.example.json`: GHCR exact-digest와 lifecycle 정책
- `github-actions-ghcr-publish-lifecycle.json`: owner-only image publish 기록
- `review/isolated-image-pull-validation-v333.json`: isolated runtime 검증 증거
- `review/neon-readonly-connectivity-v336.json`: secret 없는 Neon Direct/Pooler TLS·read-only 검증 증거
- `reverse-proxy/`, `secrets/`, `isolated-validation/`: 각 경계 설명

## 현재 상태

```txt
image supply-chain verification: complete
isolated pull/runtime/cleanup: complete
production deployment plan review: complete
provider/region/ingress class selected: Render Singapore / Neon Singapore / Render HTTPS
Neon project/read-only connectivity: created/verified
Render resource/deployment secret inputs: unresolved
production deployment approval/execution: no/no
```

기존 capacity 계약의 PostgreSQL `max_connections` review 후보 40과 external reverse proxy 경계를 유지합니다. image pull/build의 공급망 단계는 완료됐지만 production host의 실제 pull과 Compose 적용은 아직 실행하지 않았습니다.

실제 배포 전에는 `docs/current/PRODUCTION_DEPLOYMENT_PLAN.md`의 입력을 모두 확정하고, 실행 준비 commit의 정확한 SHA를 기호가 별도 승인해야 합니다. DB/Alembic mutation, volume 삭제, 자동 deploy는 포함하지 않습니다.
