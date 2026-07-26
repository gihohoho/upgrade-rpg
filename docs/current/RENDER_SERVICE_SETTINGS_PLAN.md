# Render Web Service 실행 계획 — v346

## 현재 결론

Render Web Service 생성·첫 배포에 필요한 설정, exact image, Neon 초기화, 로컬 환경값 준비가 모두 완료됐습니다. 하지만 Render에는 아직 서비스가 없고 환경변수도 주입하지 않았습니다.

다음 단계는 이 준비 상태가 담긴 clean pushed `main` 커밋의 정확한 40자리 SHA를 기호가 승인하는 것입니다. 정적 계약은 `deploy/render-service-settings.example.json`, 값이 없는 예시는 `deploy/render.production.env.example`입니다.

## 확정 설정

| 항목 | 값 |
|---|---|
| Service | Web Service / Existing Image |
| Name | `upgrade-rpg-api` |
| Region / plan | Singapore / Free / 1 instance |
| Image | `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1` |
| Registry credential | `upgrade-rpg-ghcr-read` |
| Port | `8000` |
| Platform health | `/api/v1/health` |
| Manual DB health | `/api/v1/health/db` 한 번 |
| Command override / pre-deploy | 없음 / 없음 |
| Auto deploy / disk | 꺼짐 / 없음 |
| Public URL | Render managed `onrender.com` HTTPS |
| Custom domain / payment | 보류 / 변경 없음 |

platform health는 DB를 포함하지 않아 Neon cold start 때문에 Render가 불필요하게 재시작하는 일을 막습니다. DB 연결은 첫 배포 후 `/api/v1/health/db`를 한 번 수동으로 확인합니다.

## 환경변수 준비

비밀이 아닌 고정값 11개와 secret key 3개(`DATABASE_URL`, `JWT_SECRET_KEY`, `ADMIN_WRITE_DEV_KEY`)를 사용합니다. 실제 값은 Git/Docker 제외 `deploy/.env.production`에만 준비됐습니다.

- `DATABASE_URL`: Neon direct endpoint 기반 `postgresql+asyncpg`, TLS query 없음
- TLS: 앱이 system CA와 hostname verification을 강제로 적용
- JWT/admin secret: 서로 다른 CSPRNG 값, 각각 43자 이상
- DB pool: size 2, overflow 0, pre-ping 켜짐
- CORS: 첫 backend-only 검증에서는 `[]`

`tools/prepare_render_local_environment.py --inspect-local`은 값이나 endpoint를 출력하지 않고 이 조건을 다시 검사합니다.

사용자 승인 뒤에는 같은 도구의 `--verify-execution-approval` 모드가 clean pushed `main`, exact 40자리 SHA, 서비스 이름, exact image, 단일 deploy action을 모두 확인합니다. 이 관문 자체는 Render를 변경하지 않습니다.

## exact-SHA 승인에 포함되는 실행

1. clean pushed `main`과 승인 SHA가 정확히 같은지 확인
2. Render에 `upgrade-rpg-api` Web Service 한 개 생성
3. 검토된 non-secret과 로컬 secret 3개 주입
4. 검증된 exact image로 최초 deploy 한 번 실행
5. `/api/v1/health`가 정상화될 때까지 기다림
6. `/api/v1/health/db`를 한 번 읽기 확인
7. `onrender.com` 주소와 secret 없는 결과만 sanitized evidence에 기록
8. command override, pre-deploy, auto deploy가 없음을 확인

## 승인에 포함되지 않는 실행

- DB create/delete/restore/reset/seed/write와 Alembic 작업
- 다른 image 또는 tag 사용
- custom domain, DNS, 결제수단 변경
- 자동 retry, 두 번째 deploy, 자동 migration
- 인증/API write logic, Vue write, 게임 콘텐츠·밸런스 변경

실패하면 서비스 상태를 보존한 채 멈추고 원인을 검토합니다. 자동으로 다시 deploy하거나 서비스를 삭제하지 않습니다.

무료 서비스는 idle 시 잠들어 첫 요청 cold start가 발생할 수 있는 개인용 public preview이며 SLA production으로 취급하지 않습니다.
