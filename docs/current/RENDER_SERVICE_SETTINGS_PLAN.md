# Render Web Service settings plan — v340

## 결론

Render 설정값은 검토됐지만 **현재 exact digest로 Web Service를 만들면 안 됩니다**. 현재 image에는 Neon hostname을 시스템 CA로 검증하는 SQLAlchemy `asyncpg` SSLContext가 없고, `deploy/production.env.example`에는 `ENVIRONMENT=production`, `DEBUG=false`, `PORT=8000`이 빠져 있습니다.

먼저 bootstrap을 고쳐 새 exact-digest image를 게시하고 isolated 검증해야 합니다. 그 뒤 Neon 초기화가 끝나야 Render 생성 단계로 이동합니다.

정적 계약은 `deploy/render-service-settings.example.json`입니다. 실제 secret이나 Neon endpoint는 이 문서와 계약에 기록하지 않습니다.

## 추천 설정

| 항목 | 추천값 | 이유 |
|---|---|---|
| Service type | Web Service | 공개 HTTPS API |
| Source | Existing Image | 검증된 GHCR image 사용 |
| Name | `upgrade-rpg-api` | 짧고 역할이 명확함, owner 확인 필요 |
| Region | Singapore | Neon AWS Singapore와 같은 지역 |
| Instance | Free / 1개 | 개인 preview, 월 고정비 $0 |
| Image | bootstrap 수정 후 새 exact digest | 현재 v338 digest는 Neon verify-full runtime 미지원 |
| Registry credential | `upgrade-rpg-ghcr-read` | 이미 read:packages only로 저장됨 |
| Docker command | override 없음 | image의 Uvicorn CMD 재사용 |
| Port | `8000` | image CMD와 일치 |
| Health path | `/api/v1/health` | 앱 생존 확인, DB cold start와 분리 |
| DB health | `/api/v1/health/db` 수동 확인 | transient Neon wake-up으로 Render가 재시작하는 것 방지 |
| Persistent disk | 없음 | Free에서 미지원, DB는 Neon에 저장 |
| Pre-deploy command | 없음 | Free Web Service에서 미지원, migration 자동 실행 금지 |
| Auto-deploy | 없음 | Existing Image는 auto-deploy 미지원 |
| Custom domain | 보류 | 첫 단계는 Render managed `onrender.com` HTTPS |

## 환경변수

비밀값이 아닌 고정값:

```txt
APP_NAME=Upgrade RPG Backend
ENVIRONMENT=production
DEBUG=false
PORT=8000
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=[]
DB_POOL_PRE_PING=true
DB_POOL_SIZE=2
DB_MAX_OVERFLOW=0
DB_POOL_TIMEOUT_SECONDS=30
DB_POOL_RECYCLE_SECONDS=300
```

Render에만 저장할 secret key:

```txt
DATABASE_URL
JWT_SECRET_KEY
ADMIN_WRITE_DEV_KEY
```

`DATABASE_URL`은 Neon direct endpoint를 사용하는 SQLAlchemy `postgresql+asyncpg` 형식입니다. 실제 host/user/password는 문서, Git, 로그에 기록하지 않습니다. 단일 worker가 SQLAlchemy QueuePool을 이미 사용하므로 runtime도 direct 연결을 사용해 PgBouncer와 asyncpg prepared statement의 이중 pooling 복잡성을 피합니다.

`CORS_ORIGINS=[]`는 backend-only 첫 검증용입니다. 공개 frontend 주소가 생기기 전에는 임의 origin을 허용하지 않습니다.

## 생성 전 gate

다음이 모두 끝나기 전에는 `Create Web Service` 또는 `Deploy Web Service`를 누르지 않습니다.

1. production SSLContext/bootstrap과 env inventory 수정
2. 관련 smoke와 Neon SQLAlchemy read-only 호환성 검사
3. 새 GHCR exact digest 게시
4. 새 image isolated pull/runtime 검증
5. Neon `neondb` restore + v295 stamp + read-only 검증
6. 서비스 이름 owner 확인
7. Render 생성 준비 commit의 정확한 40자리 SHA owner 승인

## 첫 배포 후 확인

1. Render deploy event가 새 exact digest를 사용했는지 확인
2. `/api/v1/health`가 2xx인지 확인
3. `/api/v1/health/db`를 한 번 수동 확인
4. container가 non-root UID 65532와 single worker로 실행되는지 확인
5. 자동 migration, pre-deploy command, custom command가 없는지 확인
6. 생성된 `onrender.com` 주소를 기록하되 secret은 기록하지 않음

Free Web Service는 15분 유휴 후 잠들며 첫 요청에 cold start가 있을 수 있습니다. image-backed 서비스는 자동 갱신되지 않으므로 이후 배포도 새 exact digest를 별도 검토·수동 적용합니다.

## 공식 근거

- Render Existing Image와 수동 deploy: https://render.com/docs/deploying-an-image
- Web Service port와 image-backed auto-deploy 제한: https://render.com/docs/web-services
- Free Web Service 제한: https://render.com/docs/free
- HTTP health check 동작: https://render.com/docs/health-checks
- Free에서 사용할 수 없는 pre-deploy command: https://render.com/docs/deploys
