# Production provider selection — v335

## 결론

비용을 가장 우선하는 개인 프로젝트 1차 배포 조합은 아래로 선택합니다.

| 역할 | 선택 | 지역 | 월 고정비 |
|---|---|---|---:|
| FastAPI 컨테이너 | Render Free Web Service | Singapore | $0 |
| PostgreSQL | Neon Free, PostgreSQL 16 | AWS Singapore (`aws-ap-southeast-1`) | $0 |
| 공개 HTTPS | Render가 발급하는 `onrender.com` 주소와 managed TLS | global edge | $0 |
| DB 관리 도구 | 현재 설치된 pgAdmin 계속 사용 | 기호 PC | $0 |

예상 월 고정비는 **$0**입니다. 처음에는 Render에 결제수단을 등록하지 않습니다. 무료 한도를 넘으면 추가 과금 대신 서비스가 일시 중지되는 경계를 선택합니다.

이 구성은 공식 SLA가 있는 상용 운영 구성이 아니라 **개인용 공개 preview**입니다. 무료 Render는 15분 동안 요청이 없으면 잠들며 다음 요청에서 다시 켜지는 데 약 1분이 걸릴 수 있습니다. 무료 Neon도 유휴 상태에서 잠들 수 있습니다.

정적 계약은 `deploy/production-provider-selection.example.json`, fail-closed 검사는 `tools/check_production_provider_selection.py`에 있습니다.

## 이 조합을 고른 이유

- Render는 `linux/amd64` prebuilt image와 private GHCR credential을 지원하므로 이미 검증한 exact digest를 그대로 지정할 수 있습니다.
- Render Singapore와 Neon AWS Singapore를 맞춰 한국에서의 지연시간과 DB 왕복 시간을 줄입니다.
- Render가 기본 HTTPS 주소와 TLS 종료를 제공하므로 첫 배포에 도메인 구매, DNS 설정, 별도 reverse proxy 서버가 필요 없습니다.
- Neon Free는 시간 제한 없이 무료로 시작할 수 있고 프로젝트당 월 100 CU-hours, 데이터 0.5 GB, 6시간 restore history를 제공합니다.
- Neon은 PostgreSQL `verify-full`을 공식 지원합니다. 실제 endpoint가 생기면 image의 system trust store 또는 Render secret file을 사용해 인증서 체인을 live 확인한 뒤 경로를 고정합니다.
- Render dashboard secret과 registry credential을 사용하므로 실제 DB URL, JWT key, admin key, GHCR token을 Git에 넣지 않습니다.
- pgAdmin은 Neon 연결에도 사용할 수 있으므로 새 DB GUI를 설치할 필요가 없습니다.

## 비교에서 제외한 안

### Render 무료 DB

Render 무료 PostgreSQL은 30일 후 만료되고 backup을 제공하지 않으므로 게임 데이터를 둘 장소로 선택하지 않습니다.

### Koyeb 무료 Web + 무료 DB

무료 Web Service 자체는 좋은 후보지만 Koyeb 무료 DB는 월 활성 compute 5시간 제한입니다. 또한 Starter 리소스 사용에는 유효한 결제수단이 필요해 이번 “무과금 위험 최소” 기준에서는 Render + Neon보다 불리합니다.

### Fly.io + Neon

Fly.io는 저렴하지만 새 조직에 결제 카드가 필요하고 항상 실행되는 VM 비용이 0원이 아닙니다. 무료 preview가 안정화된 뒤 항상 켜진 서비스가 필요할 때 다시 비교합니다.

## 유지되는 안전 경계

- image는 `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2`만 사용합니다.
- image-backed service를 수동으로 배포하고 auto-deploy는 켜지 않습니다.
- backend instance/worker는 1/1입니다.
- 실제 endpoint, 비밀번호, PAT, JWT key, admin key는 Git과 문서에 기록하지 않습니다.
- DB 생성·schema/data 이식·restore·Alembic 작업은 이번 선택에 포함되지 않습니다. 별도 계획과 승인이 필요합니다.
- 실제 Render/Neon resource 생성과 첫 배포 전에 실행 준비 commit의 정확한 40자리 SHA 승인을 다시 받습니다.
- v334 production deployment checker는 실제 값이 아직 없으므로 계속 `production-deploy-plan-reviewed-inputs-blocked`를 반환해야 합니다.

## 다음 단계

기호가 아래 두 계정에 로그인하거나 무료 가입을 완료합니다.

1. Render: 무료 Hobby workspace, 결제수단은 추가하지 않음
2. Neon: Free plan

로그인 완료 뒤 Codex가 화면을 함께 보면서 Singapore 지역 선택, 빈 resource 설정 초안, exact image, secret 이름, health path를 준비합니다. resource 생성 버튼을 누르기 전에는 비용과 DB mutation 범위를 다시 확인합니다.

```txt
provider selection: complete
production resources created: no
deployment approval ready/approved/executed: no/no/no
next safe stage: owner-connect-render-and-neon-accounts
```

## 공식 근거

- Render 무료 조건: https://render.com/docs/free
- Render private/prebuilt image: https://render.com/docs/deploying-an-image
- Render Singapore region: https://render.com/docs/regions
- Render HTTPS Web Service: https://render.com/docs/web-services
- Render secret: https://render.com/docs/configure-environment-variables
- Neon Free 가격/한도: https://neon.com/pricing
- Neon Singapore region: https://neon.com/docs/introduction/regions
- Neon `verify-full`: https://neon.com/docs/security/security-overview
- Neon restore history: https://neon.com/docs/introduction/history-window
- Koyeb DB 한도: https://www.koyeb.com/docs/databases
- Koyeb 결제수단 조건: https://www.koyeb.com/docs/reference/organizations
- Fly.io 가격과 카드 조건: https://fly.io/docs/about/pricing/
