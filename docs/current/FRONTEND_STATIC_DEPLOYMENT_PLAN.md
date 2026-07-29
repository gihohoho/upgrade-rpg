# Frontend Static Deployment and CORS Recovery Result — v355

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

Static Site `srv-d9iu337aqgkc73am4lh0`와 deploy `dep-d9iu33faqgkc73am4m3g`는 exact commit `b13b1775093716800d7361ee1e8f94d8112eefc1`로 Live입니다. v349 recovery SHA 승인 뒤 backend CORS deploy도 정확히 한 번 실행해 exact origin 적용에 성공했습니다.

## 안전한 공개 묶음

`tools/build_legacy_static_site.mjs`는 다음 파일만 `frontend/legacy-dist`에 복사합니다.

- `index.html`
- `admin.html`
- `src/` 아래 `.js`, `.css`
- `src/assets/` 아래 `.png`(현재 AI 특수장비 아이콘 23개 포함)

backend, deploy, docs, tools, Git 정보, `.env`, production secret, `src/**/*.md`는 공개 묶음에 들어가지 않습니다. 출력 폴더는 Git과 Docker build context에서도 제외합니다. 빌드는 symlink, 출력 폴더 밖 참조, 빠진 local asset, token·DB endpoint 형태 문자열을 발견하면 실패합니다.

## 로컬과 공개 API 분리

`src/api/runtime-config.js`가 `game-api-client.js`보다 먼저 실행됩니다.

- `127.0.0.1`, `localhost`, `::1`, `file://`: 기존 local API `http://127.0.0.1:8000/api/v1` 유지
- 그 밖의 HTTPS host: public API `https://upgrade-rpg-api.onrender.com/api/v1` 고정

따라서 현재 로컬 주소는 계속 그대로 쓸 수 있습니다.

- 게임: `http://127.0.0.1:5500/index.html`
- 관리자: `http://127.0.0.1:5500/admin.html`

## CORS와 관리자 경계

backend Render 환경변수 `CORS_ORIGINS`는 `["https://gihohoho-upgrade-rpg.onrender.com"]`으로 저장됐습니다. recovery deploy `dep-d9ivfmvlk1mc73fbcv40`는 40.1초 만에 Live가 됐고 health GET과 OPTIONS preflight는 모두 200이며 exact `Access-Control-Allow-Origin`을 반환합니다.

v350 당시 공개 게임의 CORS 오류는 해결됐지만 `/api/v1/game/master-data` 464,098-byte 응답이 약 1.98초와 1.83초로 frontend의 1.5초 제한을 초과해 기존 JS 데이터로 폴백했습니다. v351에서 timeout을 5초로 늘리고 backend gzip을 적용한 뒤 v355 공개 배포에서 1,346ms·gzip·no-fallback을 확인해 browser master-data 통합을 완료했습니다.

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

## v350 recovery 실행 결과

기호가 exact SHA `e64d42d812d78de023dc6cbd7f960263bc1c2d15`를 승인했습니다. CORS 행의 현재 `[]`를 먼저 표시하고, Edit에서 exact origin으로 전체 교체한 뒤 포커스를 이동해 폼 값과 14개 unique key를 재확인했습니다. `Save and deploy`는 정확히 한 번 실행했고 추가 retry는 없었습니다.

배포 뒤 actual value와 preflight를 재확인해 recovery 성공을 확정했습니다. 공개 관리자 새 탭에서는 이전 `RpgAdminFieldHelp is not loaded` 로그가 재현되지 않았습니다. frontend 재배포는 실행하지 않았습니다.

추가 Render 환경변수 변경이나 provider deploy가 필요해지면 새 준비 commit의 정확한 40자리 SHA를 기호가 승인한 뒤에만 실행합니다.

## 콘텐츠 작업 시작 기준 — v355 충족

v350 당시에는 콘텐츠 추가·수정을 시작하기 좋은 시점이 아니었습니다. 아래 두 조건은 v355에서 모두 충족됐고 v356에서 첫 장비 공식 변경을 시작했습니다.

1. 공개 게임이 backend master-data를 timeout·폴백 없이 로드: 완료
2. 관리자 guarded 콘텐츠 작업 흐름이 안전하게 검증됨: 완료

## 필요할 수 있는 사용자 조치

지금 필요한 extension·권한·설치는 없습니다. 최신 다음 단계는 `CURRENT_STATUS.md`의 v357 static-only 배포 gate 준비를 따릅니다.
