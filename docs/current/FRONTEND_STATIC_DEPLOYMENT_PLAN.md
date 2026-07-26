# Frontend Static Deployment Plan — v348

## 결론

현재 실제 게임과 관리자 화면은 Vue shell이 아니라 루트 `index.html`, `admin.html`, `src/`입니다. 따라서 첫 공개 frontend는 Render Free Static Site로 이 legacy 화면을 그대로 배포합니다.

- 추천 서비스 이름: `gihohoho-upgrade-rpg`
- 예상 게임 주소: `https://gihohoho-upgrade-rpg.onrender.com/index.html`
- 예상 관리자 주소: `https://gihohoho-upgrade-rpg.onrender.com/admin.html`
- production API: `https://upgrade-rpg-api.onrender.com/api/v1`
- build command: `node tools/build_legacy_static_site.mjs`
- publish directory: `frontend/legacy-dist`
- auto-deploy: 꺼짐
- custom domain/DNS/payment: 변경 없음

실제 Render Static Site 생성과 backend CORS 변경은 아직 실행하지 않았습니다. 준비 commit의 정확한 40자리 SHA를 기호가 승인한 뒤에만 실행합니다.

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

Static Site의 exact origin이 예상대로 확정된 뒤 backend Render 환경변수 `CORS_ORIGINS`를 그 origin 하나만 포함하도록 바꾸고 backend를 한 번 재배포해야 브라우저 API 연동이 됩니다.

`admin.html` 자체는 공개되지만 frontend에는 `ADMIN_WRITE_DEV_KEY`를 넣지 않습니다. 공개 관리자 화면은 read-only 확인 용도입니다. 실제 관리 write는 승인하지 않았고, 공개 운영 관리자 인증/RBAC를 별도로 설계하기 전에는 production write 도구로 취급하지 않습니다.

## exact-SHA 승인 뒤 실행 범위

1. clean/pushed `main`과 승인 SHA 일치 확인
2. Render에서 private GitHub repository 연결
3. Free Static Site 1개 생성, auto-deploy 비활성화
4. 승인 exact commit으로 최초 static deploy 1회
5. 실제 `onrender.com` origin 확인
6. backend `CORS_ORIGINS`에 exact frontend origin만 설정
7. backend CORS 설정 deploy 1회
8. `index.html`, `admin.html`, browser CORS, read-only API 확인
9. secret 없는 evidence 기록

실패하면 현재 provider 상태를 보존하고 중단합니다. 자동 retry, 추가 deploy, DB/Alembic write, admin write, secret 주입, custom domain/DNS, payment 변경은 승인 범위 밖입니다.

## 필요할 수 있는 사용자 조치

지금 필요한 extension이나 설치는 없습니다. 실행 시 Render가 private repository 접근을 다시 확인하라고 표시하는 경우에만 기호가 Render GitHub App의 `upgrade-rpg` repository 접근을 확인해야 합니다.
