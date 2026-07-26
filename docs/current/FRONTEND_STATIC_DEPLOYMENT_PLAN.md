# Frontend Static Deployment Result and Recovery Plan — v349

## 결론

실제 게임과 관리자 화면은 Vue shell이 아니라 루트 `index.html`, `admin.html`, `src/`입니다. 승인된 v348 준비 SHA로 Render Free Static Site에 이 legacy 화면을 배포했습니다.

- 서비스 이름: `gihohoho-upgrade-rpg`
- 게임 주소: `https://gihohoho-upgrade-rpg.onrender.com/index.html`
- 관리자 주소: `https://gihohoho-upgrade-rpg.onrender.com/admin.html`
- production API: `https://upgrade-rpg-api.onrender.com/api/v1`
- build command: `node tools/build_legacy_static_site.mjs`
- publish directory: `frontend/legacy-dist`
- auto-deploy: 꺼짐
- custom domain/DNS/payment: 변경 없음

Static Site `srv-d9iu337aqgkc73am4lh0`와 deploy `dep-d9iu33faqgkc73am4m3g`는 exact commit `b13b1775093716800d7361ee1e8f94d8112eefc1`로 Live입니다. backend CORS deploy도 승인 범위에서 정확히 한 번 실행했지만 값이 적용되지 않아 회복이 필요합니다.

## 안전한 공개 묶음

`tools/build_legacy_static_site.mjs`는 다음 파일만 `frontend/legacy-dist`에 복사합니다.

- `index.html`
- `admin.html`
- `src/` 아래 `.js`, `.css`

backend, deploy, docs, tools, Git 정보, `.env`, production secret, `src/**/*.md`는 공개 묶음에 들어가지 않습니다. 출력 폴더는 Git과 Docker build context에서도 제외합니다. 빌드는 symlink, 출력 폴더 밖 참조, 빠진 local asset, token·DB endpoint 형태 문자열을 발견하면 실패합니다.

## 로컬과 공개 API 분리

`src/api/runtime-config.js`가 `game-api-client.js`보다 먼저 실행됩니다.

- `127.0.0.1`, `localhost`, `::1`, `file://`: 기존 local API `http://127.0.0.1:8000/api/v1` 유지
- 그 밖의 HTTPS host: public API `https://upgrade-rpg-api.onrender.com/api/v1` 고정

따라서 현재 로컬 주소는 계속 그대로 쓸 수 있습니다.

- 게임: `http://127.0.0.1:5500/index.html`
- 관리자: `http://127.0.0.1:5500/admin.html`

## CORS와 관리자 경계

Static Site의 exact origin은 확정됐습니다. backend Render 환경변수 `CORS_ORIGINS`에 `["https://gihohoho-upgrade-rpg.onrender.com"]`을 입력하고 deploy `dep-d9iu4g3rjlhs73fiv570`를 한 번 실행했지만, 배포 뒤 실제 값은 `[]`로 남았습니다. 그래서 preflight는 HTTP 400 `Disallowed CORS origin`이고 공개 게임은 backend API 대신 기존 JS 데이터로 폴백합니다.

`admin.html` 자체는 공개되지만 frontend에는 `ADMIN_WRITE_DEV_KEY`를 넣지 않습니다. 공개 관리자 화면은 read-only 확인 용도입니다. 실제 관리 write는 승인하지 않았고, 공개 운영 관리자 인증/RBAC를 별도로 설계하기 전에는 production write 도구로 취급하지 않습니다.

## 승인된 v348 실행 결과

1. clean/pushed `main`과 승인 SHA 일치 확인: 성공
2. Render GitHub App을 private `gihohoho/upgrade-rpg` 단일 저장소로 연결: 성공
3. Free Static Site 1개 생성, auto-deploy 비활성화: 성공
4. 승인 exact commit으로 최초 static deploy 1회: Live
5. 실제 `onrender.com` origin 확인: 성공
6. backend `CORS_ORIGINS` 입력과 backend deploy 1회: deploy는 Live, 실제 값은 `[]`로 남아 적용 실패
7. `index.html`, `admin.html`: HTTP 200 및 화면 렌더링 확인
8. browser CORS/read-only API: 실패
9. static raw byte SHA-256: 세 핵심 자산 모두 approved source와 일치
10. 자동 retry·두 번째 deploy: 실행하지 않음

실패 정책에 따라 현재 provider 상태를 보존하고 중단했습니다. 자동 retry, 추가 deploy, DB/Alembic write, admin write, secret 주입, custom domain/DNS, payment 변경은 실행하지 않았습니다.

## 다음 exact-SHA 회복 범위

새 준비 commit의 정확한 40자리 SHA를 기호가 승인하기 전에는 backend 환경변수나 배포를 다시 변경하지 않습니다. 다음 승인 범위는 CORS 행의 현재 값을 먼저 표시해 `[]`를 확인하고, Edit에서 exact origin으로 전체 교체한 뒤 포커스를 이동해 Render 폼 상태에 반영됐는지 재확인하고, `Save and deploy`를 정확히 한 번 실행하는 focused recovery입니다.

이전 시도는 masked 값 상태에서 textarea DOM에는 새 값이 보였지만 Render가 저장할 form state에 반영되지 않은 것으로 추정합니다. 이는 원인 추정이며, 회복 실행 전·후 actual value와 preflight를 다시 확인합니다. 관리자 `RpgAdminFieldHelp is not loaded` 관찰도 같은 브라우저 검증에서 재확인하되 frontend 재배포는 별도 승인 없이는 하지 않습니다.

## 필요할 수 있는 사용자 조치

지금 필요한 extension이나 설치는 없습니다. GitHub App의 `upgrade-rpg` 단일 저장소 접근 확인도 완료됐습니다. 필요한 사용자 조치는 새 v349 회복 준비 commit의 정확한 40자리 SHA 승인뿐입니다.
