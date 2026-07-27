# Security rotation and GitHub gates — v349

## Render GitHub App repository access — 2026-07-26

- 기호가 GitHub `Confirm access`를 완료했습니다.
- Render GitHub App은 개인 계정 `gihohoho`에서 `upgrade-rpg` 단일 저장소만 접근하도록 선택했습니다.
- 모든 저장소 접근은 허용하지 않았습니다.
- 이 확인 과정에서 새 token/PAT/secret을 문서·Git·로그에 기록하지 않았습니다.
- Static Site auto-deploy는 꺼져 있으며 승인되지 않은 commit을 자동 배포하지 않습니다.

## Secret 원칙

실제 secret 값은 적지 않습니다. token, PAT, Docker credential, production `.env`, CA/cert/key를 Git·채팅·로그·artifact에 넣지 않습니다. 나중에 사용한 credential이 생기면 사용 완료 후 회전·폐기 여부를 이 문서에 기록합니다.

## Neon database credential rotation — 2026-07-22

- Neon Free PostgreSQL 16 AWS Singapore 프로젝트 생성 직후 최초 `neondb_owner` connection string이 채팅에 노출됐습니다.
- 기호가 Neon Console에서 해당 역할 비밀번호를 즉시 재설정해 최초 credential과 connection string을 무효화했습니다.
- 노출된 값은 Git, 로컬 파일, Docker image, Render, GitHub secret에 저장하거나 사용하지 않았습니다.
- 새 direct/pooled URL은 채팅으로 받지 않고 Git/Docker 제외 경로 `deploy/.env.production`에서만 로컬 입력받습니다.
- 새 URL 입력 전까지 Neon 연결 검사, DB 생성, schema/data write, migration을 실행하지 않았습니다.
- 새 URL은 Git/Docker 제외 로컬 파일에 입력했고 Direct/Pooler 모두 TLS 1.3 인증서·호스트 검증과 read-only transaction을 통과했습니다.
- sanitized evidence에는 endpoint·URL·password를 기록하지 않았고 DB write·create, schema change, restore, Alembic은 실행하지 않았습니다.

## Production deployment approval boundary

- 운영 배포 계획 검토는 완료했지만 production host/DB/CA/proxy/domain/secret/network/rollback 입력이 미확정이므로 approval ready는 `false`입니다.
- 개인 비공개 저장소의 environment에는 native required reviewer가 없고 admins can bypass가 `true`이므로 실제 deploy 준비 commit의 정확한 SHA를 source-controlled owner approval로 다시 확인합니다.
- 실제 값은 Git 밖의 승인된 secret/deployment platform에만 넣고 final Compose render 결과에도 secret을 출력하지 않습니다.
- 첫 배포는 이전 production image가 없으므로 실패 시 proxy route를 철회하고 새 backend만 중지합니다. DB, CA, network, volume은 보존합니다.
- DB/Alembic mutation, `docker compose down -v`, 자동 retry/deploy는 승인 범위 밖입니다.

## Render application secrets — v346

- 2026-07-26에 Render용 `JWT_SECRET_KEY`와 `ADMIN_WRITE_DEV_KEY`를 로컬 CSPRNG로 각각 생성했습니다.
- 두 값은 서로 다르고 43자 이상이며 Git/Docker 제외 `deploy/.env.production`에만 있습니다.
- Neon direct URL에서 query 없는 SQLAlchemy `postgresql+asyncpg` `DATABASE_URL`을 만들었고 endpoint·role·password 일치를 값 출력 없이 검사했습니다.
- 실제 값은 Git, 문서, 채팅, 로그, artifact에 기록하지 않았고 Render에도 아직 주입하지 않았습니다.
- 승인된 v346 exact SHA로 Render secret store에 3개 secret을 전달했고 값은 화면·로그·evidence에 출력하지 않았습니다.
- 첫 deploy가 Live인 뒤 `/api/v1/health/db`를 한 번 확인했으며 credential 값은 응답이나 로그에 나타나지 않았습니다.
- 값이 노출되거나 Render 계정 접근이 의심되면 JWT/admin key를 새로 생성해 Render에 교체하고 서비스를 한 번 재배포합니다. Neon credential은 Neon Console에서 별도로 회전합니다.

## Render GHCR credential rotation — v338

- Render workspace는 `Hobby (legacy)`이고 payment method가 없습니다.
- 기존 GitHub CLI OAuth token을 Render에 저장하지 않습니다.
- dedicated classic PAT note는 `render-upgrade-rpg-ghcr-read`, scope는 `read:packages` only, 만료일은 2027-07-23입니다.
- `repo`, `write:packages`, `delete:packages`는 허용하지 않습니다.
- token 생성·Render 저장·exact-digest `Connect`는 사용자 action-time 승인을 받아 2026-07-23에 실행했습니다.
- 첫 PAT는 브라우저 검사 출력에 노출된 것을 감지했습니다. Render에는 저장하지 않았고 즉시 GitHub에서 폐기했습니다. 값은 이 문서에 기록하지 않습니다.
- 교체 PAT는 화면·로그·파일 출력 없이 Render `upgrade-rpg-ghcr-read` credential로 직접 전달했습니다.
- verified exact digest `Connect`는 성공했고 서비스 설정 화면까지 진입했습니다.
- Web Service, env secret, payment method, deploy는 생성·주입·변경·실행하지 않았습니다.
- credential은 Render에서 실제 private GHCR pull이 더 이상 필요 없거나 2027-07-23 이전 회전 시 폐기합니다.

## GitHub gate 상태

2026-07-22T12:49:50Z live API 재확인:

- external action allowlist와 full-length SHA enforcement 정상
- GitHub-owned/verified creator blanket false
- default `GITHUB_TOKEN`: contents/packages read-only
- Actions PR create/approve false
- fork write token와 secret 전달 false
- `ghcr-production-publish`: main-only, secrets 0, variables 0
- required reviewer/prevent self-review: 비공개 개인 저장소 제약으로 unavailable
- environment admins can bypass: true

따라서 owner-only source-controlled two-step을 사용합니다. `run_attempt=1`, single dispatch, immediate closure, 정확한 `closureCommitSha`, rerun 금지를 유지합니다.

### v342 v341 image 게시와 gate closure — 2026-07-26

- owner 승인 preparation: `fb231afa5081f5bfd7b459081a58bc5acd6699df`
- authorization / immediate closure / evidence: `f5d69c1bbef101cc9124b9dede18c844ef80b59c` / `ebb5ef46e3115bc358d62d93a64002b8711f4232` / `cf9e0bab121186d2ac51f889f807348cc46f192c`
- workflow run `30180738530`, `run_attempt=1`, actor `gihohoho`, conclusion `success`
- artifact IDs `8625485901`, `8625478503`; exact digest `sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1`
- local/registry Trivy HIGH·CRITICAL 0건, SLSA provenance/SPDX SBOM, Cosign OIDC sign/verify를 확인했습니다.
- lifecycle은 `attempt-recorded`, gate `false`로 닫혔고 rerun은 금지합니다.
- 실제 token 값은 출력·문서화하지 않았으며 GitHub `GITHUB_TOKEN`과 기존 Docker credential store만 사용했습니다.
- Neon restore/stamp와 Render create/deploy는 실행하지 않았고 image approval을 해당 작업에 재사용하지 않습니다.

### v341 게시 준비 lifecycle 보완 — 2026-07-26

- 승인된 `789599bfe1a26cad5d8b3d80ee6a9613c5e48576`의 lifecycle이 이전 `attempt-recorded`라 workflow의 preparation-parent 조건을 충족하지 못했습니다.
- workflow를 dispatch하지 않았고 GHCR login/build/push도 새로 실행하지 않았습니다.
- 이전 성공 run `29909291344`과 관련 SHA/digest/signature evidence를 다섯 번째 history로 보존했습니다.
- 새 attempt 슬롯은 `preparation-closed`, gate `false`, approval `null`, `not-dispatched`로 초기화했습니다.
- focused 보완 commit의 새 exact SHA 승인 전에는 authorization을 열거나 workflow를 실행하지 않습니다.

## 최신 evidence

- approved preparation `b35dfacf427162b348a6bd29eb030778edc7741c`
- authorization/closure/record `04e002060e576f19f4d8687b33635a414486206d` / `64e5ae0f5e5385ba00df16bb10ac33789ca3760a` / `303a2ed01c69c29894efdcde4ead6c2291c3d8bc`
- run `29883012957`: validation/build/SBOM 성공 후 Trivy에서 failure
- vulnerability 27건: Debian HIGH 18, CRITICAL 6, Python HIGH 3
- artifact `8515504259`, SHA-256 `6a5dfd4cd96754fd365323c7c6a7d1edf18542b5e5729e44220d7bf21ace4c50`, 만료 `2026-08-05T01:26:39Z`
- publish skipped: login/push/provenance/Cosign 미실행, registry mutation 없음

## v328 보안 준비

- Alpine 3.23 exact linux/amd64 digest와 musllinux binary-only hash lock을 채택했습니다.
- 최종 runtime에서 pip/setuptools/wheel/ensurepip과 사용되지 않는 JWT 의존성을 제거했습니다.
- 로컬 Trivy 0.70의 `--ignore-unfixed=false` HIGH/CRITICAL gate는 0건으로 통과했습니다.
- gate 완화나 예외 추가는 하지 않았고 새 workflow도 실행하지 않았습니다.
- 새 preparation SHA 승인 뒤 authorization 직전에 GitHub live 설정을 4시간 이내 기준으로 다시 확인합니다.

## 4차 run 보안 결과

- 2026-07-22T02:37:10Z allowlist/full SHA/default read-only/fork token·secret false/environment main-only를 재확인했습니다.
- GHCR login과 push가 실행되어 digest `sha256:6e4aefad0cdf1767670b7f736477dd9e00f17bf49a03fa471828df6667c41149`가 존재합니다.
- provenance/SBOM은 존재하지만 SLSA v1 경로 검사 실패로 exact-digest Trivy와 Cosign이 실행되지 않았습니다.
- unsigned·미검증 digest는 production reference에 넣거나 deploy하지 않습니다.
- workflow의 `SLSA.buildType` 검사만 `SLSA.buildDefinition.buildType`으로 바꾸는 focused fix가 후보입니다.

현재 필요한 extension·설치는 없습니다. `gh` keyring의 기존 계정 token은 만료 상태지만 Windows Git 자격 증명을 명령별 `GH_TOKEN`으로만 사용해 `repo`/`workflow` 작업을 완료했고 token 값을 저장·출력하지 않았습니다. 이 token에는 `read:org`와 `read:packages`가 없지만 현재 evidence 기록에는 필요하지 않습니다. 나중에 로컬에서 GHCR package metadata를 직접 조회해야 할 때만 `read:packages` 권한을 요청합니다.

## v330 preparation 보안 상태

- 4차 run의 login/push/digest 증거를 lifecycle history에 보존했습니다.
- 새 lifecycle은 `preparation-closed`, gate `false`, approval `null`, not-dispatched입니다.
- provenance 검사는 `SLSA`/`buildDefinition` 객체와 `buildDefinition.buildType`을 순서대로 fail-closed 확인합니다.
- workflow source/semantic/per-step SHA-256 잠금을 새 내용으로 갱신했습니다.
- 새 exact preparation SHA 승인 전에는 authorization, workflow, GHCR login/push를 실행하지 않습니다.

## v331 verified candidate 보안 결과

- 2026-07-22T09:41:21Z repository Actions/allowlist/full SHA/default token/fork/environment 설정을 재확인했습니다.
- run `29909291344`의 exact-digest Trivy 결과는 0건이고 SLSA v1 provenance/SBOM 검사가 통과했습니다.
- Cosign keyless sign/verify와 certificate identity/issuer 검증이 성공했습니다.
- verified digest는 `sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2`입니다.
- production reference, local pull, container 시작, deploy는 미실행이며 별도 승인 전에 실행하지 않습니다.

## v332 production reference 정적 준비

- `deploy/production.env.example`의 `BACKEND_IMAGE`는 검증된 exact digest로 고정했습니다.
- checker는 tag, placeholder, 다른 digest로 바뀌면 fail-closed합니다.
- 실제 secret·managed DB 주소·provider CA·network 값은 계속 placeholder입니다.
- reference는 runtime에 적용하지 않았고 Docker pull·container 시작·deploy도 실행하지 않았습니다.

## v333 local GHCR credential과 isolated 검증

- 기호가 `gihohoho` 계정으로 GitHub CLI 웹 로그인을 완료했고 OAuth scope `read:packages`를 확인했습니다.
- token 값은 출력·파일·Git·채팅·artifact에 기록하지 않고 `gh auth token | docker login ... --password-stdin`으로 Docker credential store에 전달했습니다.
- private GHCR exact digest pull과 isolated container 검증은 성공했습니다.
- 임시 container/network/local image는 제거했지만 GitHub CLI keyring과 Docker credential store의 GHCR 로그인은 남아 있습니다.
- 로컬 GHCR 접근이 더 이상 필요 없을 때 `docker logout ghcr.io`와 필요 시 `gh auth logout -h github.com -u gihohoho`를 별도 보안 정리 단계로 검토합니다. 지금 임의 logout하면 다음 승인 작업을 방해할 수 있어 자동 실행하지 않았습니다.
- 비활성 `konghjin` 계정의 만료 keyring 항목은 이번 작업에서 사용하거나 삭제하지 않았습니다.
- production secret/CA/cert/key, 실제 DB, production network는 사용하지 않았습니다.

## v352 v351 backend image 게시 준비 게이트 — 2026-07-26

- GitHub Actions repository 설정은 selected actions, full-SHA 고정, 기본 read 권한, fork write token·secret 차단 상태를 read-only로 재확인했습니다.
- `ghcr-production-publish` environment는 `main` custom branch policy를 유지하며 secret·variable은 0개입니다.
- 개인 비공개 저장소 제약상 native required reviewer가 없으므로 source-controlled exact-SHA owner approval을 계속 사용합니다.
- v341 성공 게시 run `30180738530`은 여섯 번째 `attemptHistory` 항목으로 보존했습니다.
- 현재 v351 게시 lifecycle은 `preparation-closed`, gate `false`, approval `null`, `not-dispatched`입니다.
- v352 준비 SHA 승인 전에는 workflow dispatch, GHCR mutation, Docker isolated 실행, Render deploy를 하지 않습니다.
- 승인 후에도 범위는 backend image 1회 게시와 SBOM·Trivy·provenance·Cosign·isolated 검증까지입니다. Render backend exact-image와 frontend static 배포는 새 digest 확인 뒤 별도 exact-SHA 승인을 받습니다.
- 실제 token/PAT/secret 값은 조회 결과, 문서, Git, 로그, artifact에 기록하지 않았습니다.

## v353 v351 backend image 게시·isolated 완료 — 2026-07-27

- 승인 preparation `b48dfd0751b12b1b3afb6474f9d35359ba2f8177`을 authorization `7578eb665c03ee0fcb9399929328ce684cdd1b31`에서 정확히 사용했습니다.
- workflow run `30226905547`은 run_attempt=1, actor `gihohoho`, conclusion `success`이며 같은 authorization SHA의 추가 run은 없습니다.
- gate는 run 접수 직후 closure `5d547126322dbe3c235e855cc9c2f7337342ae36`에서 닫혔고 evidence `5c842deec6d1f496679a144897f485b07428810b`에 최종 결과를 기록했습니다.
- exact digest `sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac`은 Trivy HIGH·CRITICAL 0, SLSA provenance, SPDX-2.3 SBOM, Cosign OIDC sign/verify를 통과했습니다.
- private GHCR pull과 isolated non-root/read-only/internal-network runtime 검증 후 임시 container/network/local image를 제거했습니다. 기존 PostgreSQL은 healthy입니다.
- 실제 token/PAT/secret/격리용 환경값은 Git·문서·채팅·artifact에 기록하지 않았습니다.
- Render backend/static deploy, DB/Alembic/admin write, 콘텐츠 변경은 실행하지 않았습니다.
- 다음 provider release는 별도 v354 준비 commit의 정확한 SHA 승인을 요구합니다.

## v355 Render deploy hook 회전 — 2026-07-27

- Render backend와 Static Site 설정 화면이 마스킹된 deploy hook 값을 브라우저 검사 출력에 포함하는 것을 감지했습니다.
- 두 값은 Git·파일·정제 evidence에 저장하거나 deploy에 사용하지 않았습니다.
- backend deploy hook과 Static Site deploy hook을 각각 즉시 재발급해 검사 출력에 포함된 이전 값을 폐기했습니다.
- 재발급된 새 값은 조회·복사·기록하지 않았습니다.
- hook 재발급으로 추가 deploy는 발생하지 않았습니다.
- 관련 sanitized evidence: `deploy/review/render-v351-provider-release-v355.json`
