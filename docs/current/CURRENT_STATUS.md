# Current Status — v336

## 현재 결과

```txt
latest: v336.neon-readonly-connectivity-verified-render-onboarding-required
strict result: neon-direct-pooled-readonly-connectivity-verified
next safe stage: owner-connect-render-and-review-database-initialization-plan
deployment safety baseline: v334.production-deploy-plan-reviewed-inputs-blocked
baseline result: production-deploy-plan-reviewed-inputs-blocked
baseline next stage marker: select-production-targets-and-complete-executable-deploy-plan
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR repository: ghcr.io/gihohoho/upgrade-rpg-backend
production deployment approval ready/approved/executed: no/no/no
```

## 비용 최소 공급자 선택

- runtime: Render Free Web Service, Singapore, 512 MB/0.1 CPU, 단일 instance
- database: Neon Free PostgreSQL 16, AWS Singapore (`aws-ap-southeast-1`)
- public HTTPS: Render가 발급하는 `onrender.com` 주소와 managed TLS
- deployment: private GHCR의 exact digest를 사용하는 manual image-backed service
- fixed monthly cost: $0
- payment method: Render에 처음에는 등록하지 않음
- classification: SLA production이 아닌 개인용 public preview

Render 무료 app은 15분 유휴 뒤 잠들고 첫 요청에서 약 1분의 cold start가 생길 수 있습니다. Neon Free는 프로젝트당 월 100 CU-hours, 0.5 GB storage, 6시간 restore history 범위입니다. 상세 근거와 비교는 `PRODUCTION_PROVIDER_SELECTION.md`, 정적 계약은 `deploy/production-provider-selection.example.json`에 있습니다.

## Neon onboarding checkpoint — 2026-07-22

- Neon Free PostgreSQL 16 AWS Singapore 프로젝트 생성 완료
- Neon Auth 비활성 선택
- 채팅에 노출된 최초 `neondb_owner` 비밀번호 재설정·폐기 완료
- 새 direct/pooled URL은 채팅·Git·앱·배포 플랫폼에 주입하지 않고 로컬 제외 파일에만 저장
- Git/Docker 제외 로컬 입력 파일: `deploy/.env.production`
- Direct/Pooler 모두 PostgreSQL 16.14, TLS 1.3 인증서·호스트 검증, read-only transaction 통과
- sanitized evidence: `deploy/review/neon-readonly-connectivity-v336.json`

## 아직 하지 않은 것

- Render 계정 로그인과 Web Service 생성
- 계획상 `rpg_game` 데이터베이스 생성
- GHCR `read:packages` 전용 credential 생성·주입
- JWT/admin secret 생성·주입
- production CORS origin 확정
- DB schema/data 초기화·restore·Alembic 작업
- production deploy

Neon resource와 read-only 연결 검증은 완료됐지만 Render resource와 배포 플랫폼 secret 주입, DB/schema/data 준비가 남아 있으므로 v334 deployment plan의 required input은 계속 `unresolved`입니다.

## 검증된 배포 후보

- exact reference: `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2`
- GitHub Actions run `29909291344`: SBOM, Trivy HIGH/CRITICAL 0, provenance, Cosign sign/verify 성공
- isolated evidence: `deploy/review/isolated-image-pull-validation-v333.json`
- source-controlled lifecycle gate: `deploy/github-actions-ghcr-publish-lifecycle.json`
- lifecycle: `attempt-recorded`, `publishReviewerGateReady=false`
- CI credential: GitHub Actions `GITHUB_TOKEN`
- 개인 비공개 저장소 required reviewer는 없으므로 exact-SHA owner approval을 유지

## 안전 경계

- backend replicas/workers 1/1, PostgreSQL TLS `verify-full`, automatic deploy/migration 금지
- actual secret/token/PAT/password/CA/cert/key를 Git·채팅·로그·artifact에 기록하지 않음
- DB create/delete/restore/reset/seed/write와 Alembic mutation은 별도 구체적 요청·승인 전 금지
- 인증/API write, Vue Preview/Apply/write, 게임 콘텐츠·밸런스 변경 금지
- resource 생성과 실제 deploy 전 실행 준비 commit의 정확한 40자리 SHA 승인 필요

## 다음 단계

기호가 Render Hobby에 로그인합니다. Render 결제수단은 추가하지 않습니다. 로그인 완료 뒤 Codex가 계정 화면을 확인하고 Web Service 생성 직전 설정과 별도 DB 초기화 계획을 준비합니다. 현재 필요한 로컬 extension이나 설치는 없습니다. 서버 재시작도 필요하지 않습니다.
