# v344.neon-restore-verified-stamp-recovery-preparation-ready

- 승인된 v343 SHA로 Neon `neondb`에 pinned backup을 단일 트랜잭션 restore 한 번 실행했습니다.
- 22 application tables / 748 rows / schema digest가 일치했고 legacy data digest 차이에서 stamp 전에 안전하게 중단했습니다.
- 원인은 verified rehearsal `Asia/Seoul`과 Neon `GMT`가 timezone-aware datetime을 다른 offset 문자열로 반환한 session-timezone-dependent 해시였습니다.
- aware datetime을 UTC로 정규화한 application data digest는 verified rehearsal과 Neon이 `4ea23cfd2446b522cc9e85e2a8520160427cf8e3987d9b6ab04f4b99fbf6c00c`로 일치합니다.
- v344 recovery 도구는 `pg_restore` 재실행을 금지하고 새 exact-SHA 승인 뒤 restored state 재검증과 exact v295 stamp만 허용합니다.
- Alembic stamp와 Render 생성·배포는 아직 실행하지 않았습니다.

# v343.neon-initialization-preparation-ready-execution-gated

- Neon direct 대상의 exact-SHA-gated restore/stamp 도구와 focused smoke를 추가했습니다.
- 도구는 clean pushed `main`, exact preparation SHA, target, backup SHA, revision, action을 모두 확인하고 단일 트랜잭션 restore와 exact v295 stamp만 허용합니다.
- 읽기 전용 preflight에서 `neondb`의 0 public table / no Alembic 상태와 asyncpg·PostgreSQL 16/libpq `verify-full` 연결을 확인했습니다.
- Windows libpq의 `sslrootcert=system` 호환 오류는 공개 Windows 시스템 CA를 Git 제외 로컬 PEM으로 export해 해결했습니다.
- 실제 Neon restore/stamp/write와 Render Web Service 생성·배포는 실행하지 않았고, 다음 단계는 v343 준비 commit의 별도 exact-SHA owner 승인입니다.

# v342.v341-image-publish-isolated-verified-neon-init-approval-required

- owner가 승인한 preparation `fb231afa5081f5bfd7b459081a58bc5acd6699df`의 직계 자식 authorization `f5d69c1bbef101cc9124b9dede18c844ef80b59c`로 workflow run `30180738530`을 한 번만 실행했습니다.
- run 접수 직후 closure `ebb5ef46e3115bc358d62d93a64002b8711f4232`로 gate를 닫고, 성공 결과를 evidence `cf9e0bab121186d2ac51f889f807348cc46f192c`에 기록했습니다.
- build, SPDX SBOM, Trivy HIGH/CRITICAL 0건, BuildKit SLSA provenance/SBOM, exact-digest Trivy 0건, Cosign keyless sign/verify가 모두 통과했습니다.
- verified digest는 `sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1`, artifact IDs는 `8625485901`, `8625478503`입니다.
- isolated `linux/amd64` runtime에서 UID 65532, Python 3.11.15, system CA 119개, read-only rootfs, health 200을 확인하고 container/network/local image를 모두 정리했습니다.
- Neon restore/stamp와 Render 생성·배포는 실행하지 않았고, 다음 단계는 Neon 초기화 실행 준비 commit과 별도 exact-SHA 승인입니다.

# v335.cost-minimum-provider-selection-account-onboarding-required

- 2026-07-22 공식 가격·제품 문서를 비교해 개인 프로젝트 비용 최소 조합을 Render Free Web Service Singapore + Neon Free PostgreSQL 16 Singapore로 선택.
- 월 고정비 $0, Render 결제수단 미등록, `onrender.com` managed HTTPS, private GHCR exact digest 수동 image deploy를 고정.
- Render 무료 app cold start와 Neon 무료 storage/compute/restore 한계를 SLA production으로 과장하지 않고 개인용 public preview로 명시.
- 선택 계약, 공식 근거, fail-closed checker와 mutation smoke를 추가하고 실제 계정/resource/endpoint/secret/DB/deploy는 생성·변경하지 않음.
- 다음 단계는 기호의 Render/Neon 로그인이고, resource 생성·DB 초기화·deploy는 계속 별도 범위와 exact-SHA 승인을 요구.

# v334.production-deploy-plan-reviewed-inputs-blocked

- verified image와 v333 isolated evidence를 기준으로 production deploy 순서, exact-SHA 승인, 중단·rollback 계약을 정적 JSON과 fail-closed checker로 추가.
- production host, managed PostgreSQL, provider CA, reverse proxy/domain/certificate, secret injection, edge network, first-deploy rollback 입력이 미확정이라 approval ready/approved/executed를 `no/no/no`로 유지.
- GitHub Actions selected-only/full SHA, default token read-only, publish environment main-only 상태를 재확인하고 native reviewer 없음/admin bypass 가능 상태를 exact-SHA 승인 경계에 반영.
- `docs/`를 current/guides/contracts/archive/handoff로 재분류하고 root 단계 기록과 완전 동일한 archive 사본을 제거.
- `tools/` 루트의 obsolete `smoke_*` 사본 134개를 제거하고 실행되는 canonical smoke를 `tools/smoke/` 아래로 통합; 문서 구조와 production plan smoke를 core 목록에 반영.
- 루트의 오래된 v320 changelog와 backend readiness는 archive로 이동하고, 오래된 v316 ZIP과 빈 `.agents` 폴더를 제거.
- PostgreSQL local backup과 Alembic local review artifact는 보존하고 실제 production resource, DB, Alembic, DNS/proxy를 변경하지 않음.

# v333.isolated-image-pull-runtime-validation-complete-deploy-blocked

- 기호의 별도 승인과 GitHub CLI OAuth `read:packages` 인증으로 private GHCR exact digest pull 성공.
- `linux/amd64`, UID 65532, Python 3.11.15, pip 제거 상태와 exact image ID/digest 일치 확인.
- internal network, host port/volume 없음, read-only rootfs, `/tmp` tmpfs, cap-drop ALL, no-new-privileges 및 resource limit 조건에서 `/api/v1/health` 200 검증.
- `/health/db`, 실제 DB, Alembic, production secret/CA/network는 사용하지 않음.
- 첫 CORS JSON shell quoting 실패 자원을 정리한 뒤 지원되는 문자열 형식으로 재검증 성공.
- 임시 container/network/local image를 모두 제거하고 기존 PostgreSQL healthy 확인.
- sanitized evidence `deploy/review/isolated-image-pull-validation-v333.json` 추가; production deploy는 계속 미승인·미실행.

# v332.verified-digest-production-reference-static-prepared

- verified image `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2`를 `deploy/production.env.example`의 `BACKEND_IMAGE`에 정적으로 고정.
- production checker 세 개가 exact approved digest만 허용하고 placeholder·tag·다른 digest를 fail-closed하도록 갱신.
- actual secret·managed DB·provider CA·network 값은 placeholder로 유지하고 Docker pull·container·deploy는 실행하지 않음.
- local `Failed to fetch` 원인을 PostgreSQL `127.0.0.1:55432` 미실행과 legacy `127.0.0.1:5500` 서버 미실행으로 확인.
- 기존 local PostgreSQL과 프로젝트 루트 `5500` 정적 서버를 시작해 health/db/master-data와 legacy `index.html`·`admin.html` 브라우저 검증을 통과.
- Codex가 프론트·백엔드·legacy 정적 서버와 기존 local PostgreSQL dependency를 필요에 따라 직접 시작·중지·재시작하고, legacy API 통합 검증은 `file://`나 Vue `5173`이 아닌 root `5500` 주소를 사용하도록 계속 적용 규칙에 고정.
- 콘텐츠·코드·DB 개발은 가능하되 이후 코드/image 포함 변경은 새 image 공급망 검증이 필요하고 schema 변경은 Alembic·배포 순서를 별도 승인하도록 handoff에 기록.

# v331.fifth-owner-only-attempt-recorded-verified-candidate

- exact preparation `36e8720a53ef7ff6a8334de6bc99646998d63fc9` 승인 후 authorization `26a11356e33c978afa8cd8a4881500fa62cdbc5c`을 single-dispatch로 실행.
- run `29909291344` 접수 즉시 closure `1c4a982b2a35d3d45f59e7d9faefcdecca69e6c5`로 gate를 닫고 rerun 금지.
- validation/local build/SBOM/Trivy, GHCR login/build/push, SLSA v1 provenance/SBOM, exact-digest Trivy 0건, Cosign sign/verify 모두 성공.
- verified digest `sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2`와 artifacts `8525220616`/`8525254543` 기록.
- evidence `1f0340ddfcf3c8a74cf14110d5957627d4c5d38a`로 lifecycle `attempt-recorded`, gate `false`, signature verified 상태 확정.
- production reference 변경, pull, container 시작, deploy는 별도 승인 전에 실행하지 않음.

# v330.slsa-v1-provenance-path-preparation

- run `29886540317`의 실패 로그와 registry provenance artifact에서 SLSA v1 `buildType` 위치를 `SLSA.buildDefinition.buildType`으로 재확인.
- workflow가 `SLSA`/`buildDefinition` 객체를 fail-closed로 검사한 뒤 `buildDefinition.buildType`을 확인하도록 focused fix.
- workflow source/semantic/per-step SHA-256 잠금을 갱신하고 구형 경로로 되돌리는 mutation smoke를 추가.
- 4차 run의 push/digest/artifact 증거를 `attemptHistory`에 보존하고 새 lifecycle을 `preparation-closed`, gate `false`, approval `null`, not-dispatched로 초기화.
- 새 workflow는 미실행이며 preparation commit의 exact 40자 SHA 승인 전에 authorization을 열지 않음.

# v329.fourth-owner-only-attempt-recorded-provenance-inspection-failed

- exact preparation `13b15409929d77b4e6209481596e4f4550a22ba5` 승인과 single-dispatch run `29886540317` 기록.
- validation/local build/SBOM/local Trivy와 GHCR login/build/push 성공.
- pushed digest `sha256:6e4aefad0cdf1767670b7f736477dd9e00f17bf49a03fa471828df6667c41149` 기록.
- SLSA v1 `buildType`이 `SLSA.buildDefinition.buildType`에 있으나 workflow가 구형 경로를 검사해 failure.
- exact-digest Trivy/Cosign 미실행, signature 미검증, artifacts `8516735247`/`8516749365` 보존.

# v328.alpine-musllinux-runtime-minimization-preparation

- Python 3.11.15 Alpine 3.23 `linux/amd64` manifest digest로 production base를 갱신하고 multi-stage/UID 65532 runtime으로 최소화.
- Ubuntu CI용 manylinux와 production용 musllinux binary-only SHA-256 lock을 분리.
- 최종 runtime에서 pip/setuptools/wheel/ensurepip을 제거하고 미사용 `python-jose[cryptography]` 전이 의존성을 제거.
- 로컬 linux/amd64 import/read-only 검사와 Trivy 0.70 HIGH/CRITICAL `--ignore-unfixed=false` gate 0건 통과.
- 기존 세 workflow 시도를 history로 보존하고 새 lifecycle을 `preparation-closed`, gate `false`, not-dispatched로 초기화.

# v326.dockerfile-bootstrap-fixed-retry-preparation-publish-gated

- 기호의 승인에 따라 `backend/Dockerfile.production` bootstrap pip download의 `--python-version 3`을 `3.11`로 focused fix.
- workflow run `29716038891`, `29877813770`의 실패 증거를 lifecycle `attemptHistory`에 모두 보존.
- lifecycle을 새 `preparation-closed`로 초기화하고 gate를 `false`, 현재 run을 `not-dispatched`로 유지.
- 새 preparation commit의 exact 40-character SHA 승인 전에는 authorization/workflow 실행 금지.

# v325.second-owner-only-attempt-recorded-failed-pre-registry-image-build

- 기호가 승인한 preparation `2f77ebf0f60a39c936509df26f903995f0c62967`의 direct-child authorization `7e69555b8b653c406b322fb5c8f23e550751d72c`을 만들고 workflow를 정확히 한 번 dispatch.
- run `29877813770` 접수 직후 closure `5479e6b14826b3a0f2b6d0c3beb0e2142ca22c94`으로 gate를 닫고 rerun하지 않음.
- 이전 실패 지점인 workflow bootstrap dependency와 repository checks 통과.
- `backend/Dockerfile.production:22`의 남은 bootstrap `--python-version 3` 때문에 local linux/amd64 image build에서 `pip==26.1.2`를 찾지 못해 failure.
- SBOM/Trivy와 publish job은 미실행 또는 skipped; GHCR login/push, artifact, digest, signature, registry mutation 없음.
- 다음 focused fix 후보는 Dockerfile bootstrap target 한 곳을 `3.11`로 바꾸는 것이며 아직 사용자 승인 전.

# v324.bootstrap-fixed-retry-preparation-publish-gated

- 기호가 승인한 focused fix로 workflow bootstrap wheel 대상 Python을 `3`에서 `3.11`로 수정.
- workflow source/semantic hash와 validate dependency-install run-step hash를 새 값으로 잠금.
- checker 요약의 고정 `workflow executed: no` 표기를 lifecycle 증거 기반 동적 값으로 수정해 prior workflow `yes`, registry mutation `no`를 구분.
- 첫 실패 evidence commit `1f12ea59eb54385337557e9754f86731ec53d253`와 run `29716038891`을 `priorAttemptEvidence`로 보존한 새 retry `preparation-closed` lifecycle 추가.
- authorization에서 GitHub live 설정 값은 그대로 유지하면서 `recheckedAtUtc`만 더 새로운 실제 확인 시각으로 갱신하도록 변경해 4시간 제한과 SHA 승인 절차의 충돌을 해소.
- gate는 계속 `false`; 새 preparation SHA 승인 전 workflow 재실행 금지.

# v323.first-owner-only-publish-attempt-recorded-failed-pre-registry

- 기호가 정확히 승인한 preparation SHA `350bbd085f1cf636810d75ddcbb5321e0791256c`의 direct-child authorization commit `32e5102877851ace06e1c0ed3bcb48310b8d65b6`을 만들고 workflow를 정확히 한 번 dispatch.
- run `29716038891` 접수 직후 closure commit `362f5f1901d234b5b86f2a7cefdabd28ac61f896`으로 gate를 즉시 닫고 rerun하지 않음.
- validate job의 dependency 설치에서 bootstrap pip download `--python-version 3`과 `pip==26.1.2`의 Python `>=3.10` 조건 불일치로 failure 확인.
- build/publish jobs는 skipped; GHCR login/build/push, artifact, digest, signature는 발생하지 않음.
- lifecycle을 `attempt-recorded`로 종결하고 focused fix 후보를 `--python-version 3.11`로 기록. 수정 구현 전 별도 사용자 승인이 필요.

# v322.owner-only-single-run-lifecycle-hardened-publish-gated

- 기호가 `f4788acf5455b07169320bd29f43ddf92ff1d5ad` 준비 commit을 정확히 승인했지만, 실행 전 재감사에서 open gate를 허용하지 않는 checker, rerun/중복 dispatch 방어 부재, authorization-parent 연결 부재, 계획 밖 Docker build record artifact, post-push 실패 증거 미보존을 발견.
- 과거 승인은 `priorApprovedPreparationSha` 이력으로만 보존하고, 보안 계약이 바뀐 v322 preparation-fix commit의 새 exact 40-character SHA를 다시 승인받도록 fail-closed 상태 유지.
- 기본 closed인 `deploy/github-actions-ghcr-publish-lifecycle.json`을 추가하고 authorization commit은 승인 preparation의 direct child이면서 lifecycle 파일 하나만 바꾸도록 설계.
- repository owner, `run_attempt=1`, GitHub Actions API의 single dispatch 검증을 추가하고 workflow rerun을 금지.
- run ID 접수 직후 성공·실패를 기다리지 않고 별도 closure commit으로 gate를 닫는 immediate closure 절차를 고정.
- `DOCKER_BUILD_RECORD_UPLOAD=false`로 계획 밖 Docker build record artifact를 끄고, image push 뒤 실패해도 존재하는 digest/provenance/SBOM/Trivy/Cosign 부분 증거를 14일 보존하도록 변경. 부분 증거는 verified candidate로 취급하지 않음.
- authorization-open lifecycle을 closed root 전용 handoff smoke가 오탐으로 거부하지 않도록 정적 checker는 직접 실행하고 `SKIP_GHCR_HANDOFF_SMOKES=1 bash tools/run_smoke_core.sh`를 사용. 이 플래그는 closed 전용 세 smoke만 제외하며 앱·백엔드 전체 core smoke는 유지.
- lifecycle을 P `preparation-closed` → A `authorization-open` → C `authorization-closed-awaiting-evidence` → R `attempt-recorded` 네 상태로 보강. run 접수 즉시 C로 닫되 자기 SHA는 쓸 수 없어 `closureCommitSha=null`을 유지하고, 종료 뒤 별도 R evidence commit이 부모 C commit SHA와 run ID/URL/conclusion/digest/signature 실제 결과를 기록. non-success conclusion만으로 registry mutation/signature 미실행을 단정하지 않고 job/step 증거를 각각 확인하도록 고정.
- 2026-07-20 repository 설정을 live 재확인하고 drift로 켜져 있던 fork write token과 fork secret 전달을 모두 `false`로 복원. allowlist/full SHA/default read-only/environment main-only/secrets·variables 0/0을 재확인.
- native required reviewer/prevent self-review는 비공개 개인 저장소 제약으로 계속 없으며 owner-only 모델이 독립 reviewer와 동등하지 않음을 유지.
- workflow, GHCR login/build/push, production reference 변경, Docker/DB/Alembic mutation은 실행하지 않음. 다음 단계는 `review-and-approve-exact-preparation-fix-sha`.

# v321.owner-only-reproducibility-locked-publish-gated

- 기호가 비공개 개인 저장소의 잔여 위험을 이해하고 `owner-only-source-controlled-two-step` 승인 모델을 선택.
- CPython 3.11 Linux/amd64 application/build dependency, pip `26.1.2`, setuptools `80.10.2`, wheel `0.46.3`, Dockerfile frontend를 exact version과 SHA-256으로 잠금.
- source distribution을 금지하고 선택 wheel hash를 검증하는 dependency lock 생성기와 smoke를 추가.
- byte-for-byte deterministic image를 보장한다고 과장하지 않고 exact digest/SBOM/Trivy/provenance/Cosign 검증을 유지.
- preparation 상태에서 publish gate를 `false`로 두고 정확한 40자 SHA를 기호가 별도 승인한 뒤만 authorization을 검토하도록 문서화.
- workflow와 GHCR registry mutation은 실행하지 않음.

# v320.github-actions-ghcr-workflow-prepared-gated

- repository Actions 설정을 외부 action 8개 full-SHA allowlist와 full-length SHA 강제로 바꾸고 기본 read-only `GITHUB_TOKEN` 정책을 유지.
- `ghcr-production-publish` environment를 만들고 `main` branch rule을 적용했지만 required reviewer/prevent self-review는 미구성 상태로 기록. GitHub Free/Pro/Team의 required reviewer는 공개 저장소에서만 지원되므로 비공개 저장소에 collaborator를 추가하는 것만으로 해결되지 않음.
- `.github/workflows/publish-backend-ghcr.yml`을 작성하고 source-controlled `PUBLISH_REVIEWER_GATE_READY="false"`를 첫 단계에 두어 repository/environment variable로 우회할 수 없게 차단.
- production Dockerfile에 맞는 root build context, 공식 Trivy 0.70.0 asset SHA-256 검증, 로컬 및 pushed exact-digest HIGH/CRITICAL scan을 적용.
- BuildKit mode=max provenance/SBOM을 exact digest에서 검사한 뒤에만 Cosign keyless sign/identity·issuer verify를 수행하도록 순서를 고정.
- PyYAML duplicate-key 방지 loader, exact event/job/permission/action/step 검사와 workflow 소스·실행 의미 이중 SHA-256 잠금을 추가하고 quoted `push`, 추가 write/secret 유출 step, `|| true`, SHA/checksum/gate 변조 smoke를 통과.
- action/run step별 잠금과 parsed secret 경로 allowlist를 추가하고, `.dockerignore`에서 모든 `.env`/`*.env`/`.envrc`를 root build context에서 제외하도록 강제.
- 현재 범위형 Python dependency/build-system, unpinned pip upgrade, mutable Dockerfile frontend로 reproducible build가 보장되지 않음을 기록하고 첫 게시 전 필수 gate로 고정.
- 개발 서버 재사용, GitHub/숨김 파일 권한과 보안 회전 checklist를 AGENTS/NEXT_CHAT/current 문서에 동기화.
- workflow와 Docker/registry/DB/Alembic mutation은 실행하지 않음. 다음 단계는 `github-enterprise-cloud-required-reviewer`, `owner-only-source-controlled-two-step`, `keep-publishing-disabled` 중 게시 승인 모델 선택이며, 선택 전에는 source-controlled hard gate를 `false`로 유지.

# v319.github-connector-actions-settings-reviewed

- ChatGPT Codex Connector를 `gihohoho/upgrade-rpg` 저장소 하나에만 연결하고 Codex repository 조회를 검증.
- GitHub Actions 설정과 environment를 읽기 전용으로 검토해 현재 모든 action 허용, full-length SHA 강제 꺼짐, read-only 기본 `GITHUB_TOKEN`, publish environment 부재를 기록.
- 연결·검토 완료 상태와 아직 승인되지 않은 repository 설정/environment/workflow 변경을 분리한 v319 fail-closed 검사와 smoke 추가.
- `.github/workflows/`, workflow 실행, Docker/registry/DB/Alembic mutation은 없음.

# v318.github-actions-action-sha-candidates-reviewed

- 9개 허용 action의 2026-07-15 최신 정식 release tag와 upstream 40자리 commit SHA를 공식 GitHub 저장소에서 대조해 검토 후보로 고정.
- 검토 후보와 사용자 승인값을 분리하고 `approvedSha: null`, workflow 생성·실행 승인 `false`를 유지하는 fail-closed 검사 추가.
- Python 3.11.4와 `backend/.venv` 정상 상태를 확인하고 전체 core smoke를 끝까지 통과.
- Windows cp949 실행 차단 안내, source stamp smoke의 실제 보고서 격리, 가짜 Docker Compose render smoke 실행 호환성 문제를 수정.
- Codex GitHub 플러그인은 설치됐지만 GitHub App 설치 계정이 0개임을 확인했으며 `gihohoho/upgrade-rpg` 연결 요청을 계속 인계.
- `.github/workflows/`, workflow 실행, Docker/registry/DB/Alembic mutation은 없음.

# v317.github-actions-ghcr-static-workflow-plan

- GitHub Actions/GHCR publish의 `workflow_dispatch` only, exact main SHA, protected environment, concurrency 정적 정책 추가.
- validate/build-scan job은 `contents: read`, publish/attest/sign job만 `packages`, `attestations`, `id-token` write를 받도록 최소 permissions 설계.
- local OCI, SPDX JSON SBOM, Trivy HIGH/CRITICAL, provenance, SBOM attestation, Sigstore keyless signature와 verification을 fail-closed gate로 고정.
- 모든 action은 검토된 40자리 commit SHA가 필요하며 실제 SHA가 미승인인 동안 workflow 생성을 차단.
- ZIP/Git 명령 안내를 중단하고 Codex가 NEXT_CHAT 갱신과 add/commit/push를 직접 수행하는 협업 규칙 반영.
- 필요한 extension/repository 권한/설치는 사용자에게 요청하고 해결되지 않으면 다음 작업에서도 다시 요청하도록 인계 규칙 반영.
- `.github/workflows/`, workflow 실행, Docker/registry/DB/Alembic mutation은 없음.

# v316.codex-handoff-audit-fix

- v315 커밋의 strict checker와 실제 추적 파일을 대조해 superseded 활성 파일 정리 누락을 수정.
- 보관본이 있는 v313 문서/정책/checker와 더 이상 실행되지 않는 v313 smoke를 활성 경로에서 제거.
- 로컬 작업 폴더에서는 금지 경로의 Git 추적 여부만 확인하고, 추출된 ZIP에서는 금지 경로의 실제 존재를 계속 차단하도록 검사 모드를 분리.
- ZIP 모드에 `backend/.env` fixture를 추가해 secret 경로 검사가 fail-closed로 유지됨을 검증.
- 실제 `.env` 내용, workflow, token/PAT, Docker, registry, DB, Alembic은 읽거나 변경·실행하지 않음.

# v315.codex-ghcr-namespace-handoff-ready

- GitHub/GHCR namespace를 사용자 확인값 `gihohoho`로 고정.
- backend repository를 `ghcr.io/gihohoho/upgrade-rpg-backend`로 고정.
- Codex용 루트 `AGENTS.md`, v315 prompt/handoff, read-only checker/smoke 추가.
- CI credential 우선안을 GitHub Actions `GITHUB_TOKEN`, local credential/PAT는 deferred로 기록.
- v313/v314 이미지 정책 문서와 JSON을 archive/review로 이동하고 superseded checker를 정리.
- `docs/` 루트의 archive 중복 사본을 제거하고 현재/보관 문서 인덱스를 단일화.
- 실제 workflow, token, Docker login/pull/build/push, DB/Alembic mutation은 실행하지 않음.

# v310 문서/인수인계 정리

- current/archive 문서 구조 정리
- production secret/TLS/container static validation 준비
- 자세한 변경은 루트 `CHANGELOG.md`의 v310 항목 참조

# v308 - FastAPI/PostgreSQL runtime config hardening

- Recorded the user PC v307 `--strict --require-health` success with exact `rpg_game`, PostgreSQL 16.14, healthy Docker, and 12 production-hardening warnings.
- Added five environment-backed SQLAlchemy async pool options while preserving local defaults.
- Added FastAPI lifespan shutdown disposal with no startup migration or schema mutation.
- Added a fail-closed production settings guard for DEBUG and local/default or short JWT/admin secrets.
- Added a non-root FastAPI Dockerfile and a separate production Compose review template without Adminer or PostgreSQL host-port publication.
- Added a read-only v308 verifier, dedicated smoke, readiness/current/handoff documentation, and a new handoff ZIP.
- Did not edit the real `.env`, run Docker build/up/down, change DB schema/data, add revisions, alter API contracts, auth/write behavior, Vue, or game content.

# v307 - PostgreSQL/FastAPI deployment runtime readiness

- Added a read-only runtime readiness checker for exact `rpg_game`, `postgresql+asyncpg`, live revision, FastAPI startup mutation boundaries, Docker running/healthy state, env key inventory, and DB health contract.
- Added a production-hardening warning classification for pool policy, engine disposal lifecycle, local secrets, published Adminer/PostgreSQL ports, image digest, TLS, and FastAPI container image.
- Added a manual deployment migration runbook that keeps migrations out of server startup and requires backup, isolated rehearsal, and separate approval.
- Added dedicated v307 smoke, core registration, readiness/current/handoff documentation, and a new handoff ZIP.
- No `.env`, Docker container/volume, DB schema/data, Alembic revision/history, API route/body, auth, write logic, seed, Vue, or game content was changed.

# v304 - PostgreSQL source baseline stamp final guard

- Added an exact-source `rpg_game` baseline stamp guard with read-only pre/post inspection.
- Pinned revision, backup SHA-256, verified rehearsal result, and approved application schema/data digests.
- Added exact confirmation flags for the future source-only `stamp head` approval boundary.
- Added post-stamp recovery classification that prevents automatic retries after a partial report failure.
- Added dedicated source stamp smoke coverage and updated handoff/current-status documentation.
- Did not execute source stamp, upgrade, downgrade, DB create/drop/restore, `.env`, Docker, API/write, auth, seed, or game-content changes.

# v303 - Restore rehearsal stamp post-check recovery

- Recorded the user-approved v302 rehearsal-only stamp execution.
- Fixed the v302 post-stamp inspect bug that rejected the expected `alembic_version` table by reusing the pre-stamp validator.
- Added read-only pre/post lifecycle classification and pinned application schema/data digest verification.
- Added current source/migration validation and optional v302 local execution report matching.
- Added a report-missing recovery classification without retry, rollback, upgrade, downgrade, DB create/drop/restore, or source mutation.
- Expanded dedicated smoke and synchronized current/handoff documentation.

# v302 - Restore rehearsal baseline stamp guard ready

- Recorded the user-PC v301 source preflight success.
- Added `tools/stamp_postgres_restore_rehearsal_database.py`, pinned to `rpg_game_restore_rehearsal_v290`, `v295_initial_schema`, and exact revision SHA-256.
- Added read-only full application schema and row-content SHA-256 signatures for all 22 tables / 748 rows.
- Added postconditions allowing only `alembic_version` 1 table / 1 row while requiring source and migration DB signatures to remain identical.
- Added exact `--confirm-target` and `--confirm-revision` execution confirmations; actual stamp was not executed.
- Added dedicated simulated smoke, core registration, current/handoff documentation, and v302 ZIP handoff.
- Kept DB schema/data, `.env`, Docker resources, seed, auth, API routes/bodies, Write Guard, Preview/Apply bodies, and game content unchanged.

# v301 - Source baseline stamp read-only preflight handoff

- Recorded the user-PC v300 round-trip result: `upgrade -> downgrade base -> upgrade`, identical first/second signatures, source/rehearsal preserved.
- Added `tools/check_postgres_source_baseline_stamp_preflight.py` to revalidate source schema/data, exact backup, reviewed revision, v300 evidence, and current migration head without mutation.
- Added a dedicated smoke and registered it in core smoke.
- Updated current/handoff/root documentation to move the next safety boundary to a restore-rehearsal `stamp head` rehearsal, not the source DB.
- Kept source/rehearsal/migration DBs, `.env`, Docker resources, route paths, response bodies, auth, Write Guard, Preview/Apply bodies, and game content unchanged.

## v300.postgres-migration-roundtrip-reupgrade-ready

- v298 first upgrade와 v299 downgrade report를 고정한 두 번째 upgrade 왕복 검증 가드 추가
- 첫/두 번째 upgrade signature exact 비교 및 source/rehearsal 보존 검사
- 전용 smoke, core 등록, readiness/current/handoff 문서 v300 동기화

## v299.postgres-migration-test-downgrade-base-ready

- 사용자 PC에서 v298 isolated `upgrade head` 성공 결과 반영
- exact reviewed revision과 v298 upgrade report를 요구하는 `downgrade base` 실행 가드 추가
- target DB가 빈 `alembic_version` placeholder로 복귀하는지 검증
- source/rehearsal DB 작업 전후 보존, 자동 retry/upgrade/stamp/create/drop/restore 차단
- 전용 smoke, core 등록, readiness/current/handoff 문서 v299 동기화

## v298.postgres-initial-alembic-manual-review-upgrade-ready

- 사용자 review bundle의 exact revision SHA-256과 bundle SHA-256을 재검증
- `v295_initial_schema`를 SQLAlchemy model과 수동 교차 검토: 22 tables / 209 columns / 42 indexes / 21 FK / 6 Unique
- 타입, 길이, nullable, PK/FK/ondelete/onupdate, unique, index, server default 일치 확인
- PostgreSQL FLOAT 2개가 v289 DOUBLE PRECISION alias 정책과 일치함을 확인
- downgrade index/table 대응과 FK dependency reverse order 검증
- 검토된 revision 파일과 machine-readable manual review manifest를 프로젝트 기준 파일로 포함
- `tools/upgrade_postgres_migration_test_database.py` 추가: exact reviewed revision을 `rpg_game_migration_empty_v290`에만 `upgrade head`하도록 준비
- 실제 upgrade/downgrade/stamp/source DB mutation은 실행하지 않음
- manual review/upgrade guard smoke, core 등록, v298 문서/handoff 동기화

## v297.postgres-initial-alembic-op-f-parser-recovery

- 사용자 실제 v296 결과 `unexpected Alembic operations: upgrade=['f'], downgrade=['f']`를 재현하고 원인을 확인
- Alembic generated revision의 nested `op.f(...)`를 naming helper로 분리해 operation allowlist false positive 제거
- 실제 create/drop/index/constraint operation 검사와 execute/data/destructive operation 차단 유지
- 전용 smoke가 `op.create_index(op.f(...))`, `op.drop_index(op.f(...))`를 생성하고 `f`가 operation count에 포함되지 않음을 검증
- 실패 시 생성 revision/review artifact 정리, empty `alembic_version` placeholder 재사용, DB/env/Alembic apply 경계 유지
- v297 current/readiness/handoff 문서 동기화

## v296.postgres-initial-alembic-revision-placeholder-recovery

- v295 autogenerate가 남긴 정확히 `alembic_version` 1 table / 0 rows / no revision 상태를 안전한 recovery workspace로 인정
- `--inspect-workspace` 읽기 전용 진단과 placeholder 재사용 경계 추가
- 다른 application table/row/revision이 있으면 실행 전 차단
- upgrade/downgrade/stamp, DB create/drop/restore 미실행

# v292 - PostgreSQL empty restore rehearsal database creation tool

- Added `tools/create_postgres_restore_rehearsal_database.py` for the user-approved existence-check-and-create-empty-DB boundary.
- Requires the verified v291 backup, recomputes SHA-256, rechecks the 22-table/748-row source baseline, and checks `pg_database` before any mutation.
- Creates only `rpg_game_restore_rehearsal_v290` when absent, with owner `rpg_user`, template `template0`, and source-compatible encoding/collation/locale metadata.
- Verifies the target has zero public tables and no `alembic_version`, then confirms the source remains 22 tables / 748 rows.
- Stops when the target already exists and never runs `pg_restore`, `dropdb`, `.env` edits, Docker changes, Alembic mutations, API/auth/write changes, or game-content changes.
- Added dedicated smoke coverage, core-smoke registration, current-state documentation, and v292 handoff synchronization.

# v291 - PostgreSQL backup creation and archive verification tool

- Added `tools/create_postgres_backup.py` for the user-approved source backup step only.
- Re-runs schema/preflight gates, pins `rpg_game`/`rpg_user`/`upgrade_rpg_postgres`, streams a custom-format dump to a private partial file, validates the archive with `pg_restore --list`, and publishes it only after validation.
- Adds SHA-256, TOC, source table/row snapshot, and manifest sidecars under ignored `local-backups/postgres/`.
- Refuses overwrite/collision and does not restore, create/drop databases, change Docker resources, edit `.env`, run Alembic mutations, or change API/auth/write/game content.
- Added a dedicated smoke and core-smoke registration; the handoff ZIP excludes all backup artifacts.

# v290 - PostgreSQL backup/restore read-only preflight gate

- Added `tools/check_postgres_backup_restore_preflight.py` to re-run the schema-equivalence gate, check host/existing-container `pg_dump`, `pg_restore`, `createdb`, and `dropdb` availability, and report whether the project is ready to request backup execution approval.
- Fixed the backup policy at `local-backups/postgres/` with KST timestamped PostgreSQL custom-format dump names and SHA-256 sidecars; added `/local-backups/` to Git/Docker exclusions.
- Fixed isolated database boundaries: source `rpg_game`, restore rehearsal `rpg_game_restore_rehearsal_v290`, and empty migration test `rpg_game_migration_empty_v290`.
- Added restore before/after table and row-count comparison planning, separate empty-DB Alembic validation planning, a dedicated smoke, and core-smoke registration.
- The handoff sandbox could not connect because `psycopg` and PostgreSQL client/Docker tooling were unavailable there; this is recorded as non-authoritative and no zero-difference claim was made.
- Did not create a dump, restore data, create/drop a database, modify Docker resources, edit `.env`, create/apply/stamp migrations, or change routes/auth/write/game content.

# v289 - PostgreSQL FLOAT alias normalization and handoff cleanup

- Normalized PostgreSQL `FLOAT` aliases in the read-only schema checker so SQLAlchemy `FLOAT` and reflected `DOUBLE PRECISION` are compared as the same storage type.
- Added smoke coverage for `FLOAT`, `FLOAT(24)`, `FLOAT(25)`, `REAL`, and `DOUBLE PRECISION` normalization.
- Updated and registered the canonical next-chat handoff smoke.
- Removed generated `backend/idle_rpg_backend.egg-info/`, added `*.egg-info/` to `.gitignore`, removed duplicate `backend/env.example`, and synchronized current/root/handoff docs.
- Did not change PostgreSQL schema/data, Docker resources, `.env`, seed, Alembic revisions, routes, response bodies, authentication, or write logic.

# v288 - PostgreSQL schema equivalence read-only preflight

- Added `tools/check_postgres_schema_equivalence.py` to compare live PostgreSQL tables, columns, types, nullability, PK, FK, unique constraints, indexes, and check constraints with SQLAlchemy metadata.
- Added `docs/current/POSTGRES_SCHEMA_EQUIVALENCE_CHECK.md` and a dedicated core smoke.
- Kept DB schema/data, Docker resources, env, seed, revisions, migration apply/stamp, API contracts, auth, and write behavior unchanged.

# v287 - Windows subprocess decode fix and baseline strategy confirmation

- Fixed the user-reproduced Windows `cp949`/UTF-8 mixed Docker output `UnicodeDecodeError` with `tools/_safe_subprocess.py`.
- Applied safe decoding to PostgreSQL runtime, prerequisite, and Alembic read-only checkers.
- Recorded the actual DB result: PostgreSQL 16.14, 22 model/public tables, 748 rows, no `alembic_version`, healthy DB endpoint.
- Confirmed `existing-schema-without-alembic-baseline` and the existing-data-preserving baseline strategy.

# v286 - PostgreSQL/Alembic baseline strategy plan

- Added a decision matrix for empty DB, existing create_all schema with preserved data, and schema drift.
- Requires backup/restore rehearsal and separate empty-DB migration verification before any baseline stamp.
- Kept revision creation, upgrade, downgrade, stamp, DB schema/data, Docker resources, and env unchanged.

# v285 - PostgreSQL runtime read-only state checker

- Added `tools/check_postgres_runtime_readonly_state.py` for read-only Docker status, PostgreSQL schema/table/row counts, model-table comparison, Alembic version state, and FastAPI DB health.
- Added automatic classifications: `empty-database`, `existing-schema-without-alembic-baseline`, `schema-drift`, and `alembic-managed`.
- Added a dedicated smoke and registered it in core smoke.
- The checker never starts/stops Docker, mutates SQL data/schema, edits env, or runs migration mutation commands.

# v284 - Alembic asyncpg online env fix

- Fixed the user-reproduced `sqlalchemy.exc.MissingGreenlet` from `python -m alembic current`.
- Replaced sync `engine_from_config()` with `async_engine_from_config()`, async connection handling, and `connection.run_sync()`.
- Added `tools/check_alembic_readonly_state.py` for read-only `history`, `heads`, and `current` collection.
- Added a dedicated Alembic async env smoke and registered it in core smoke.
- Recorded that the actual backend virtualenv is `backend/.venv`.
- Kept DB schema/data, Docker volume, env, seed, revisions, migration apply/stamp, routes, API bodies, auth, and write logic unchanged.

# v283 - PostgreSQL/Alembic prerequisite checker

- Added `tools/check_postgres_alembic_prerequisites.py`, a read-only local checker for Python, virtualenv, Docker, Compose, SQLAlchemy, Alembic, asyncpg, psycopg, and required project files.
- Added `docs/current/POSTGRES_ALEMBIC_LOCAL_CHECKLIST.md` with exact install locations, `.venv` states, and dangerous commands that remain forbidden.
- The checker never connects to the DB, starts Docker, changes `.env`, or runs migrations.

# v282 - PostgreSQL/Alembic readiness report

- Added `tools/report_postgres_alembic_readiness.py` and `docs/current/POSTGRES_ALEMBIC_READINESS.md`.
- Documented 22 SQLAlchemy tables, PostgreSQL-specific types, asyncpg/psycopg responsibilities, Docker settings, and the current Alembic state with zero revisions.
- Recorded missing `versions/` and `script.py.mako`, create_all ownership, async online execution verification risk, and destructive reset/down-volume commands.
- Added `tools/smoke/backend/smoke_postgres_alembic_readiness.py`.
- Kept DB schema/data, Docker volumes, env, seed, route paths, response bodies, auth, Write Guard, write logic, and game content unchanged.

# v281 - Vue admin related-row detail navigation

- Added read-only related-row detail navigation from the relations panel.
- Preserves prior selections in a local `selectionHistory` stack and adds `이전 상세로` without changing routes or write behavior.
- Clears history when the domain/catalog selection is reset.

# v280 - Vue admin read-only relations panel

- Added `AdminMasterRelationsPanel.vue` for `GET /admin/master-data/relations`.
- Displays backend-provided relation groups, compact columns/rows, counts, limited indicators, and loading/error/empty/success states.
- Uses `limit=20`, cancels stale requests, and never requests raw JSON/assets or mutation APIs.
- Added a dedicated read-only relations/navigation smoke.
- Kept DB, env, seed, auth, route paths, API response bodies, Write Guard, Preview/Apply request bodies, and actual write logic unchanged.

# v279 - Vue admin read-only detail panel

- Added `AdminMasterDetailPanel.vue` for `GET /admin/master-data/detail`.
- Displays scalar fields, relation hints, sanitized JSON previews, asset hiding state, and warnings without calling relations or write APIs.
- Improved `/admin/requirements` summary from `-` to `준비 완료` using the existing `readOnlyOverviewReady` response field.
- Kept DB, env, seed, auth, route paths, API response bodies, Write Guard, Preview/Apply request bodies, and actual write logic unchanged.

# v278 - Vue admin catalog query controls

- Added search, enabled/disabled filtering, safe sort selection, and previous/next pagination using the existing catalog GET query contract.
- Resets filters/page when the domain changes and clears stale detail selection whenever the catalog is reloaded.
- Keeps page size at 20 and cancels stale requests with `AbortController`.
- Added no library or framework.

# v277 - Vue admin read-only catalog mini panel

- Added `AdminMasterDomainPanel.vue` for `GET /admin/master-data/domains`.
- Added `AdminMasterCatalogMiniPanel.vue` for the selected domain first page using `limit=20`, `page=1`, `sort=id_asc`.
- Added loading/error/empty/success states, domain selection, generic backend column/row rendering, and stale request cancellation.
- Added dedicated Vue read-only catalog smoke and documentation.
- Kept DB, env, seed, auth, route paths, API response bodies, Write Guard, Preview/Apply request bodies, and actual write logic unchanged.

# v276 - Vue admin read-only domain panel

- Connected `GET /admin/master-data/domains` to the Vue admin shell.
- Parsed the actual response from `payload.domains` and `payload.defaultDomain`.
- Added domain counts, retry, and loading/error/empty/success states.
- No new library or framework was added.

## v275.backend-route-map-report

- Added `tools/report_backend_route_map.py` to generate/check a deterministic backend route map without importing `app.main`.
- Added `docs/current/BACKEND_ROUTE_MAP.md` with all 27 FastAPI routes, GET/POST counts, Vue read-only candidates, and postponed Preview/Apply/write routes.
- Added `tools/smoke/backend/smoke_backend_route_map_report.py` and included it in `tools/run_smoke_core.sh`.
- Updated `frontend/vue-app/src/api/adminReadOnlyApi.js` so master-data detail/relations wrappers translate `rowId` to the backend query name `id`.
- Confirmed that route paths, API response bodies, DB, env, seed, auth, Write Guard, Preview/Apply request bodies, write logic, existing smoke/contract meaning, and game content remain unchanged.

## v274.backend-structure-plan

- Added `tools/report_backend_structure_plan.py` to generate/check a deterministic backend structure plan.
- Added `docs/current/BACKEND_STRUCTURE_PLAN.md` with current route/service/schema/model/db/core responsibilities.
- Added `tools/smoke/backend/smoke_backend_structure_plan.py` to guard that the structure plan stays up to date.
- Confirmed that route paths, API response bodies, DB, env, seed, auth, Write Guard, Preview/Apply request bodies, write logic, existing smoke/contract meaning, and game content remain unchanged.

## v272.vue-readonly-api-smoke-screen

- Added `healthReadOnlyApi` for safe `GET /health` and prepared `GET /health/db` without auto-calling DB health.
- Added `ReadOnlyApiStatusPanel.vue` to show loading/success/error states and a retry button inside the Vue shell.
- Connected `/game` to safe `GET /health` status checking and `/admin` to safe `GET /health` plus `GET /admin/requirements` status checking.
- Added `smoke_vue_readonly_api_status_panel.py` and included it in `tools/run_smoke_vue_shell.sh`.
- Kept legacy `index.html`, `admin.html`, root `src/`, route paths, API response bodies, DB, env, seed, auth, Write Guard, Preview/Apply body, write logic, and game content unchanged.

## v269.legacy-path-dependency-report

- Added `tools/report_legacy_path_dependencies.py` to generate/check a legacy path dependency report before Vue/FastAPI/DB transition work.
- Added `docs/current/LEGACY_PATH_DEPENDENCIES.md` with current high-risk legacy path references, HTML direct-load relationships, and core smoke path dependencies.
- Decided that the future Vue app should be created under `frontend/vue-app/` instead of reusing the root `src/` folder.
- Kept `admin.html`, `index.html`, existing `src/`, backend routes/services, DB, env, seed, auth, API response bodies, write guards, and actual write logic unchanged.

# v268 - Project structure transition prep

- 현재 ZIP 기준으로 프로젝트 구조를 다시 점검했습니다.
- Vue/FastAPI/DB 전환을 위해 legacy 보존 범위와 이식 후보를 정리했습니다.
- smoke/contract 경로 의존성 때문에 실제 파일 대이동은 보류했습니다.
- 다음 단계는 legacy 경로 의존성 자동 목록화와 Vue 앱 생성 위치 결정입니다.
- 런타임 코드, DB, env, seed, route path, API response body, auth, write guard, 실제 write 로직은 변경하지 않았습니다.

# v258 - Admin Workspace navigation UX

- Added an admin workspace hub that splits the page into task-first modes instead of one long mixed screen.
- Added five modes: lookup/detail, create row, edit/apply review, Preview verification, and change-log/Rollback.
- Each mode opens a guidance modal and expands only related sections while preserving all existing routes, response bodies, write guards, and backend behavior.
- Added `src/api/admin/admin-workspace-navigation.js` and `tools/smoke/frontend/smoke_admin_workspace_navigation.js`.
- The new navigation layer performs no fetch/API/apply/write calls.

# v256 - Admin Preview live API render check

- Added a read-only live Preview API render check panel to the admin Preview verification section.
- The panel calls only existing dry-run Preview API methods and renders their actual response payload through the shared Preview result summary and Diff/Snapshot renderer.
- Covered Create, Edit, Rollback, create-delete, and create-delete-restore Preview APIs.
- Added `tools/smoke/frontend/smoke_admin_preview_live_api_render_check.js` to verify allowed Preview methods, script load order, dryRun-only calls, no `confirmText`, no write headers, and no `applyAdmin*` calls.
- No DB, env, seed, auth, route path, API response body, write guard, or real write logic changes.


## v238.7 backend admin readiness/runtime fallback hotfix

- Fixed `editDraftSplitContractReady` comparing extracted v191 contract against obsolete frozen v190 status.
- Added canonical `api_router` fallback when local FastAPI/Starlette hides included routes behind an opaque root adapter.
- Preserved list-only runtime route collector compatibility for operation/response metadata contracts.
- No API path, response body, DB, or env changes.


## v238.4 backend admin runtime route nested hotfix

- FastAPI/Starlette dependency combinations that retain included routers as nested containers are now supported by the runtime route contract.
- Removed the brittle assumption that `api_router.routes` must already contain all 21 flattened admin operations.
- Runtime collection now recursively walks `routes` and nested `router.routes` while preserving prefixes.
- API paths, response bodies, DB, and env remain unchanged.

## v238.2 - Backend admin runtime route contract environment hotfix

- `tools/smoke/contracts/smoke_backend_admin_runtime_route_contract.py`가 개발자 PC의 셸 환경변수나 프로젝트 루트 `.env`에 설정된 `API_PREFIX` 값에 영향을 받지 않도록, 앱 import 전에 계약 기준값 `/api/v1`을 명시적으로 고정했습니다.
- runtime route smoke가 실제 등록 경로를 하나도 찾지 못할 경우 전체 `registered paths`를 오류 메시지에 포함하도록 진단을 강화했습니다.
- Windows Git Bash, macOS/Linux, CI에서 동일한 21개 Admin route 계약을 검사하도록 smoke 실행을 결정적으로 만들었습니다.
- API route, 응답 body, DB, backend `.env` 구조는 변경하지 않았습니다.

## v238.1 - Backend admin schema readiness hotfix

- 프론트 `ADMIN_BACKEND_SERVICE_SPLIT_CONTRACT.routeContract`에 schema/model 및 field constraint readiness marker를 추가했습니다.
- 두 readiness 값이 실제로 `true`가 되는 연결을 복구했습니다.
- 관련 smoke가 변수명 존재만 확인하지 않고 실제 marker 존재까지 검사하도록 강화했습니다.
- API/DB/env/route/schema/응답 body 변경은 없습니다.

# v236 - Backend admin schema/model contract

- `backend/app/api/routes/admin_schema_model_contract.py`를 추가했습니다.
- OpenAPI `components.schemas`의 Admin request schema 11개를 고정했습니다.
- 관리자 body route 11개와 `backend/app/schemas/admin.py` class 이름을 대조합니다.
- 쓰기 apply schema 5개의 `confirmText` / `reason` 필드와 alias를 검증합니다.
- schema drift가 발생하면 core smoke에서 즉시 실패하도록 추가했습니다.
- `getAdminBackendServiceSplitContractReadiness().splitStatus`를 `admin-schema-field-constraint-contract-v238`으로 갱신했습니다.
- `checkAdminReadOnlyPageReady().version`을 `v238.backend-admin-schema-field-constraint-contract`로 갱신했습니다.
- route path/API 응답 body 구조/DB/env 변경은 없습니다.

# v234 - Backend admin request metadata contract

- `backend/app/api/routes/admin_request_metadata_contract.py`를 추가했습니다.
- 관리자 route 21개의 query/path/body/dependency metadata contract를 추가했습니다.
- FastAPI runtime route의 request metadata와 OpenAPI request metadata를 대조합니다.
- 쓰기 route 5개의 `require_admin_write_dev_key` write guard 유지 여부를 검증합니다.
- `getAdminBackendServiceSplitContractReadiness().splitStatus`를 `admin-schema-field-constraint-contract-v238`로 갱신했습니다.
- `checkAdminReadOnlyPageReady().version`을 `v238.backend-admin-schema-field-constraint-contract`로 갱신했습니다.
- route path/schema/API 응답 body 구조/DB/env 변경은 없습니다.

# v232 - Backend admin response metadata contract

- `backend/app/api/routes/admin_response_metadata_contract.py`를 추가했습니다.
- FastAPI runtime route의 `status_code`, `response_model`, `include_in_schema` metadata를 검증합니다.
- OpenAPI summary / 200 response / 필요한 422 validation response metadata를 static operation contract와 대조합니다.
- `getAdminBackendServiceSplitContractReadiness().splitStatus`를 `admin-response-metadata-contract-v232`로 갱신했습니다.
- `checkAdminReadOnlyPageReady().version`을 `v232.backend-admin-response-metadata-contract`로 갱신했습니다.
- route path/schema/API 응답 구조/DB/env 변경은 없습니다.

# v230 - Backend admin OpenAPI route contract

- `backend/app/api/routes/admin_openapi_route_contract.py`를 추가했습니다.
- FastAPI OpenAPI schema에 노출되는 `/api/v1/admin/...` route 21개를 static operation contract와 대조합니다.
- OpenAPI `operationId`, `admin` tag, 200 response metadata가 의도치 않게 바뀌면 smoke에서 잡도록 했습니다.
- `getAdminBackendServiceSplitContractReadiness().splitStatus`를 `admin-openapi-route-contract-v230`로 갱신했습니다.
- `checkAdminReadOnlyPageReady().version`을 `v230.backend-admin-openapi-route-contract`로 갱신했습니다.
- route path/schema/API 응답 구조/DB/env 변경은 없습니다.

# v228 - Backend admin route operation contract

- `backend/app/api/routes/admin_route_operation_contract.py`를 추가했습니다.
- 관리자 route 21개의 endpoint/function name, response type marker, owner file을 contract로 고정했습니다.
- static route ownership map, route source의 `admin_ok_response(type=...)`, FastAPI runtime endpoint/name을 함께 대조합니다.
- `getAdminBackendServiceSplitContractReadiness().splitStatus`를 `admin-route-operation-contract-v228`로 갱신했습니다.
- `checkAdminReadOnlyPageReady().version`을 `v228.backend-admin-route-operation-contract`로 갱신했습니다.
- route path/schema/API 응답 구조/DB/env 변경은 없습니다.

# v226 - Backend admin runtime route contract

- `backend/app/api/routes/admin_runtime_route_contract.py`를 추가했습니다.
- FastAPI 앱에 실제 등록된 `/api/v1/admin/...` route 목록을 static route ownership map과 대조합니다.
- 관리자 route 누락/예상 밖 등록/중복 method+path 등록을 smoke에서 잡도록 했습니다.
- `getAdminBackendServiceSplitContractReadiness().splitStatus`를 `admin-runtime-route-contract-v226`으로 갱신했습니다.
- `checkAdminReadOnlyPageReady().version`을 `v226.backend-admin-runtime-route-contract`로 갱신했습니다.
- route path/schema/API 응답 구조/DB/env 변경은 없습니다.

# v218 - Backend admin route map contract

- `backend/app/api/routes/admin.py`의 legacy static-smoke marker 주석을 제거했습니다.
- 오래된 smoke가 `admin.py` 주석 대신 실제 route module/helper 파일을 검사하도록 정리했습니다.
- `backend/app/api/routes/admin_route_map_contract.py`를 추가했습니다.
- `getAdminBackendServiceSplitContractReadiness().splitStatus`를 `admin-route-map-contract-v218`으로 갱신했습니다.
- `checkAdminReadOnlyPageReady().version`을 `v218.backend-admin-route-map-contract`로 갱신했습니다.
- route path/schema/API 응답 구조/DB/env 변경은 없습니다.

# v216 - Backend admin overview route facade split

- `backend/app/api/routes/admin_overview_snapshot_routes.py`를 추가했습니다.
- `/requirements`, `/overview`, `/save-snapshots`, `/change-preview` route를 `admin.py`에서 분리했습니다.
- `admin.py`는 include-router facade로 축소했습니다.
- `getAdminBackendServiceSplitContractReadiness().splitStatus`를 `admin-route-map-contract-v218`으로 갱신했습니다.
- route path/schema/API 응답 구조/DB/env 변경은 없습니다.

## v212 - Backend admin route response data/meta helpers

- `backend/app/api/routes/admin_response_data_helpers.py`를 추가했습니다.
- `backend/app/api/routes/admin_response_meta_helpers.py`를 추가했습니다.
- `admin.py`의 반복 `data={...}` / `meta={...}` 응답 생성 코드를 helper로 분리했습니다.
- `getAdminBackendServiceSplitContractReadiness().splitStatus`를 `admin-route-data-meta-helpers-v212`로 갱신했습니다.
- `checkAdminReadOnlyPageReady().version`을 `v212.backend-admin-route-data-meta-helpers`로 갱신했습니다.
- API path/schema/envelope/DB/env 변경은 없습니다.

## v210 - Backend admin route params/error helpers

- `backend/app/api/routes/admin_route_params.py`를 추가해 관리자 route의 반복 dependency/query 기본값을 한 곳으로 모았습니다.
- `backend/app/api/routes/admin_route_error_helpers.py`를 추가해 `/admin/change-logs` route-level fallback payload 생성을 분리했습니다.
- `getAdminBackendServiceSplitContractReadiness().splitStatus`를 `admin-route-params-errors-v210`로 갱신했습니다.
- `checkAdminReadOnlyPageReady().version`을 `v210.backend-admin-route-params-error-helpers`로 갱신했습니다.
- route/schema/API/DB/env 변경은 없습니다.

# Changelog

## v208 - Backend admin route response helper

- `backend/app/api/routes/admin_response_helpers.py`를 추가했습니다.
- `backend/app/api/routes/admin.py`가 `ok_response()`를 직접 호출하지 않고 `admin_ok_response()` helper를 사용하도록 정리했습니다.
- route/schema/API/DB/env 변경 없이 응답 생성 지점만 중앙화했습니다.
- `getAdminBackendServiceSplitContractReadiness().splitStatus`를 `route-response-helper-v208`로 갱신했습니다.
- `checkAdminReadOnlyPageReady().version`을 `v208.backend-admin-route-response-helper`로 갱신했습니다.

## v206 - Backend admin config/readiness service split

- `backend/app/services/admin/admin_config.py`를 추가했습니다.
- `backend/app/services/admin/admin_readiness_service.py`를 추가했습니다.
- `AdminService` facade에 남아 있던 큰 설정/상수 묶음과 작은 readiness helper를 분리했습니다.
- `getAdminBackendServiceSplitContractReadiness().splitStatus`를 `readiness-extracted-v206`으로 갱신했습니다.
- `checkAdminReadOnlyPageReady().version`을 `v206.backend-admin-config-readiness-service-split`으로 갱신했습니다.
- route/schema/API/DB/env 변경은 없습니다.
- `tools/smoke/contracts/smoke_backend_admin_config_readiness_service_split.py`를 추가하고 core smoke에 포함했습니다.

## v205 - Backend admin config service split

- `MASTER_DATA_MODELS`, `MASTER_CATALOG_DOMAINS`, `MASTER_EDIT_ALLOWED_FIELDS`, `MASTER_CREATE_BLUEPRINT_FIELDS` 등 admin 설정 묶음을 `AdminConfigService`로 이동했습니다.
- 기존 public method와 route facade 계약은 유지했습니다.

## v204 - Backend admin shared utils service split

- `backend/app/services/admin/admin_shared_utils.py`를 추가했습니다.
- `AdminService` facade와 split service들에 흩어진 공용 helper를 shared utils로 이동했습니다.
- `getAdminBackendServiceSplitContractReadiness().splitStatus`를 `shared-utils-extracted-v204`로 갱신했습니다.
- `checkAdminReadOnlyPageReady().version`을 `v204.backend-admin-shared-utils-service-split`으로 갱신했습니다.
- route/schema/API/DB/env 변경은 없습니다.
- `tools/smoke/contracts/smoke_backend_admin_shared_utils_service_split.py`를 추가하고 core smoke에 포함했습니다.

## v203 - Backend admin edit draft service split

- `backend/app/services/admin/admin_edit_draft_service.py`를 추가했습니다.
- `preview_master_data_edit`, `apply_master_data_edit` 및 편집 초안 helper를 `AdminService`에서 분리했습니다.
- `AdminService` facade, route, schema, DB/env 계약은 유지했습니다.
- `getAdminBackendServiceSplitContractReadiness().splitStatus`를 `edit-draft-extracted-v203`으로 갱신했습니다.
- `tools/smoke/contracts/smoke_backend_admin_edit_draft_service_split.py`를 추가하고 core smoke에 포함했습니다.

## v202 - Backend admin change log service split

- `backend/app/services/admin/admin_change_log_service.py`를 추가했습니다.
- change logs 목록/상세/rollback 관련 public/helper 메서드를 `AdminChangeLogService` mixin으로 이동했습니다.
- `AdminService` facade, route path, schema/API 응답 구조는 유지했습니다.
- `/admin/change-logs` schema guard와 route exception guard는 분리 파일에서도 유지됩니다.
- `apply_admin_change_log_rollback()` 성공 경로에서 `return preview`가 누락될 수 있던 부분을 보강했습니다.
- `getAdminBackendServiceSplitContractReadiness().splitStatus`를 `change-logs-extracted-v202`로 갱신했습니다.
- `tools/smoke/contracts/smoke_backend_admin_change_log_service_split.py`를 추가하고 core smoke에 포함했습니다.
- DB schema/env 변경, DB reset, seed 재실행은 필요 없습니다.

## v201.1 - Admin change logs schema guard hotfix

- `/api/v1/admin/change-logs` 목록 조회가 로컬 개발 DB의 누락된 `admin_change_logs` 테이블/스키마 때문에 500으로 죽지 않도록 방어했습니다.
- SQLAlchemy 쿼리 실패 시 `session.rollback()` 후 `schema_unavailable` 빈 목록 payload를 반환합니다.
- 관리자 UI에 `python scripts/setup_dev_db.py --create-schema --verify` 복구 명령을 표시합니다.
- `setup_dev_db.py --verify`가 `admin_change_logs`, `admin_user_roles`, `user_save_snapshots`, `users` 카운트도 확인하도록 확장했습니다.
- `tools/smoke/frontend/smoke_admin_change_logs_schema_guard.py`를 추가하고 core smoke에 포함했습니다.

## v201 backend admin create lifecycle service split

- `backend/app/services/admin/admin_create_lifecycle_service.py` 추가
- `AdminCreateLifecycleService` mixin 추가
- create blueprint / create preview/apply / create-delete / restore 관련 메서드 이동
- `AdminService` facade, route/schema/API 응답 구조 유지
- `tools/smoke/contracts/smoke_backend_admin_create_lifecycle_service_split.py` 추가

## v200 backend admin master catalog/detail service split

- `backend/app/services/admin/admin_master_catalog_service.py` 추가
- master catalog/detail/relations 관련 백엔드 메서드 분리
- `AdminService` facade 유지
- route/schema/API 응답 구조 변경 없음
- `tools/smoke/contracts/smoke_backend_admin_master_catalog_service_split.py` 추가


## v199.1 backend admin overview/snapshots service hotfix

- v199 분리 후 `/api/v1/admin/save-snapshots`에서 500이 날 수 있던 bound-method 오류 수정
- 원인: `_count_filled_items`가 분리 파일로 이동하면서 `@staticmethod`가 누락됨
- 수정: `AdminOverviewSnapshotsService._count_filled_items`에 `@staticmethod` 복원
- 재발 방지: `tools/smoke/contracts/smoke_backend_admin_overview_snapshots_service_split.py`가 실제 `_serialize_save_snapshot_summary()` 호출까지 검사
- route/schema/DB/env 변경 없음


## v198 — backend admin service split contract

- `backend/app/services/admin_service_split_contract.py` 추가
- `tools/smoke/contracts/smoke_backend_admin_service_split_contract.py` 추가
- 백엔드 AdminService 실제 분리 전 route/schema 유지 계약 고정
- 관리자 readiness에 `backendServiceSplitContractReady` 추가

# v197 admin settings/helpers split

- `src/api/admin/admin-settings-helpers.js`를 추가했습니다.
- API base URL / admin write dev key / 현재 관리자 URL / 게임 URL / 주소 복사 helper를 `admin-page-readonly.js` 밖으로 분리했습니다.
- 기존 window 함수명 wrapper는 유지했습니다.
- `checkAdminReadOnlyPageReady().settingsHelpersExternalReady`를 추가했습니다.
- 새 smoke `tools/smoke/frontend/smoke_admin_settings_helpers_split.js`를 추가하고 core smoke에 포함했습니다.
- 기존 URL helper smoke를 새 분리 구조에 맞게 갱신했습니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.

# v196 admin field help/value hints split

- `src/api/admin/admin-field-help.js`를 추가했습니다.
- field help / value hints / equip slot label helper를 `admin-page-readonly.js` 밖으로 분리했습니다.
- 기존 window 함수명 wrapper는 유지했습니다.
- `checkAdminReadOnlyPageReady().fieldHelpExternalReady`를 추가했습니다.
- 새 smoke `tools/smoke/frontend/smoke_admin_field_help_split.js`를 추가하고 core smoke에 포함했습니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.

# v194 admin bootstrap/bindEvents readiness

- `admin-page-readonly.js`를 바로 더 분리하지 않고 bootstrap/bindEvents/window export 계약을 고정했습니다.
- `ADMIN_BOOTSTRAP_BINDING_CONTRACT`를 추가했습니다.
- `getAdminBootstrapBindingReadiness()` / `renderAdminBootstrapBindingReadiness()`를 추가했습니다.
- `checkAdminReadOnlyPageReady().bootstrapBindingReady`를 추가했습니다.
- 새 smoke `tools/smoke/frontend/smoke_admin_bootstrap_bindings_readiness.js`를 추가하고 core smoke에 포함했습니다.
- 새 쓰기 도메인 오픈 없음.
- DB schema 변경 없음, DB reset / seed 필요 없음.

## v192 - admin master catalog/detail split

- Added `src/api/admin/admin-master-catalog.js`.
- Split master catalog/detail/relations/API verify logic out of `admin-page-readonly.js`.
- Kept existing window wrappers for browser compatibility.
- Added `tools/smoke/frontend/smoke_admin_master_catalog_split.js`.

# v190 admin edit draft split contract

- `edit draft` 실제 분리 전에 API/window/DOM/확인 문구 계약을 먼저 고정.
- 다음 후보 파일명 `src/api/admin/admin-edit-draft.js` 확정.
- `getAdminEditDraftSplitContractReadiness()` / `renderAdminEditDraftSplitContractReadiness()` 추가.
- `checkAdminReadOnlyPageReady().editDraftSplitContractReady` 추가.
- 새 smoke `tools/smoke/frontend/smoke_admin_edit_draft_split_contract.js` 추가 및 core smoke 포함.
- 새 쓰기 도메인 오픈 없음.
- DB schema 변경 없음, DB reset / seed 필요 없음.

# v189.1 admin create lifecycle split hotfix

- `src/api/admin/admin-create-lifecycle.js` 신규 추가.
- 생성 설계/초안/preview/apply/lifecycle guide/batch check 구현을 외부 JS 파일로 1차 분리했습니다.
- `admin-page-readonly.js`에는 기존 window export 호환 wrapper를 유지했습니다.
- `admin.html` script 순서를 game api → layout shell → change logs → create lifecycle → admin page로 변경했습니다.
- 새 smoke `tools/smoke/frontend/smoke_admin_create_lifecycle_split.js`를 추가하고 core smoke에 포함했습니다.
- DB schema 변경, DB reset, seed 재실행은 필요 없습니다.

# v188 admin create lifecycle split contract

- create lifecycle 실제 분리 전 계약을 `contract-frozen-v188` 상태로 고정했습니다.
- 다음 후보 파일명을 `src/api/admin/admin-create-lifecycle.js`로 고정했습니다.
- 생성 초안, 생성 preview/apply, lifecycle guide, batch check 관련 API/window/DOM 계약 진단을 추가했습니다.
- 새 smoke `tools/smoke/frontend/smoke_admin_create_lifecycle_split_contract.js`를 추가하고 core smoke에 포함했습니다.
- 실제 파일 분리는 아직 하지 않았습니다.
- DB schema 변경, DB reset, seed 재실행은 필요 없습니다.


## v187

- `src/api/admin/admin-change-logs.js` 신규 추가.
- 관리자 change logs 구현을 외부 JS 파일로 1차 분리.
- `admin-page-readonly.js`에는 기존 window export 호환 wrapper 유지.
- `admin.html` script 순서를 game api → layout shell → change logs → admin page로 변경.
- 새 smoke `tools/smoke/frontend/smoke_admin_change_logs_split.js` 추가.
- DB schema 변경 없음, DB reset / seed 필요 없음.


## v184 - Admin JS Split Readiness

- 관리자 페이지에 `관리자 JS 분리 준비` 섹션을 추가했습니다.
- 실제 파일 분리는 하지 않고 script 순서, 필수 global, export 계약, 분리 후보 묶음을 진단합니다.
- `getAdminJsSplitReadiness()`와 `renderAdminJsSplitReadiness()`를 추가했습니다.
- `checkAdminReadOnlyPageReady()`에 `adminJsSplitReadinessReady`와 `adminJsSplitReadiness`를 추가했습니다.
- 첫 실제 분리 후보를 DB 쓰기와 무관한 `layout shell`로 잡았습니다.
- 새 smoke `tools/smoke/frontend/smoke_admin_js_split_readiness.js`를 추가하고 core smoke에 포함했습니다.
- 새 쓰기 도메인은 열지 않았고 DB schema 변경 없음, DB reset / seed 필요 없음.

## v183 - Admin Create Lifecycle Batch Check

- 관리자 `신규 row 생성·삭제·복원 점검` 섹션에 일괄 점검 카드를 추가했습니다.
- 현재 생성 초안을 기준으로 생성 preview → 생성 apply → 삭제 preview → 삭제 apply → 복원 preview → 복원 apply를 순서대로 실행할 수 있습니다.
- 일괄 점검 전용 확인 문구 `RUN CREATE DELETE RESTORE CHECK`를 추가했습니다.
- dev key, 생성 확인 문구, 브라우저 confirm, 기존 백엔드 preview guard를 모두 유지했습니다.
- 단계별 결과 테이블과 요약 카드를 표시합니다.
- 새 쓰기 도메인은 열지 않았고 기존 create/delete/restore guard는 유지했습니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.

## v182 - Admin Create Lifecycle Result Summary

- 생성 row 삭제 preview/apply 결과 상단에 요약 카드를 추가했습니다.
- 삭제 결과에서 현재값 불일치, 연결 검사 수, 차단 guard 수, 차단 row 수를 바로 볼 수 있게 했습니다.
- 삭제 row 복원 preview/apply 결과 상단에 요약 카드를 추가했습니다.
- 복원 결과에서 id/code 충돌, validation error, relation 값 수를 바로 볼 수 있게 했습니다.
- 백엔드 응답에 `dependencyCheckCount`, `dependencyBlockerGuardCount`, `restoreConflictCount` 보조 count를 추가했습니다.
- 새 쓰기 도메인은 열지 않았고 기존 create/delete/restore guard는 유지했습니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.

## v181 - Admin Create Lifecycle Guard Helper

- `createLifecycle` 메타데이터에 도메인별 삭제 preview 차단 기준을 추가했습니다.
- 관리자 `신규 row 생성·삭제·복원 점검` 섹션에 삭제 차단 기준 카드를 추가했습니다.
- 변경 이력 action 필터 바로가기 버튼을 추가했습니다.
- `checkAdminReadOnlyPageReady()`에 `createLifecycleDependencyGuideReady` 상태를 추가했습니다.
- 새 쓰기 도메인은 열지 않았고 기존 create/delete/restore guard는 유지했습니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.

## v180 - Admin Create Lifecycle Guide

- 관리자 페이지에 `신규 row 생성·삭제·복원 점검` 섹션을 추가했습니다.
- 생성 blueprint 응답에 `createLifecycle` 메타데이터를 추가했습니다.
- 생성/삭제/복원 가능 여부, id/code 삭제 key, combo guard, JSON/asset 잠금 필드를 한 화면에서 확인할 수 있습니다.
- 변경 이력 action 필터를 실제 저장되는 `update`, `rollback`, `create`, `create_delete`, `create_delete_restore` 기준으로 정리했습니다.
- 새 쓰기 도메인을 열지 않았고 기존 create/delete/restore guard는 유지했습니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.

## v179 - Create Apply Level and Link Tables

- `skillLevels`, `enhancementLevels`, `characterSkills` 신규 row 생성 apply 제한 오픈.
- 위 3개 도메인 생성 row 삭제/복원 allow-list 추가.
- code 없는 relation/level row라 id 기반 생성 row 삭제/복원 guard 추가.
- `skillLevels`는 `skill_code + level` 중복을 차단합니다.
- `enhancementLevels`는 `group_code + from_level`, `to_level`, 확률/비용 검증을 강화했습니다.
- `characterSkills`는 `character_code + skill_code`, `sort_order` 검증을 강화했습니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.

## v178 - Create Apply ItemTemplates and DropTableItems

- `itemTemplates`, `dropTableItems` 신규 row 생성 apply 제한 오픈.
- `itemTemplates` 생성 row 삭제 guard에 `dropTableItems.item_template_code`, `itemInstances.template_code` 연결 검사 추가.
- `dropTableItems`는 code 없는 leaf row라 id 기반 생성 row 삭제/복원 흐름을 제한 오픈.
- `dropTableItems` 생성 검증에 rate/min/max 수량 guard 추가.
- DB schema 변경 없음, DB reset / seed 필요 없음.

## v177 - Create Apply Skills and DropTables

- 신규 row 생성 apply 제한 도메인에 `skills`와 `dropTables`를 추가했습니다.
- `characters`, `enhancementGroups`, `fieldZones`, `bosses`, `skills`, `dropTables`만 실제 생성 apply가 가능합니다.
- `itemTemplates`, `dropTableItems` 생성 apply는 계속 잠금 상태입니다.
- `skills`, `dropTables` 생성 row 삭제/복원 allow-list를 추가했습니다.
- `skills` 삭제 preview에서 `skillLevels.skill_code`, `characterSkills.skill_code`, `userCharacterSkills.skill_code` 연결을 검사합니다.
- `dropTables` 삭제 preview에서 `dropTableItems.drop_table_code` 연결을 검사합니다.
- 관리자 생성 준비 UI 안내 문구를 새 allow-list에 맞춰 갱신했습니다.
- DB reset / seed는 필요 없습니다.

## v176 - Create Apply Bosses

- 신규 row 생성 apply 제한 도메인에 `bosses`를 추가했습니다.
- `characters`, `enhancementGroups`, `fieldZones`, `bosses`만 실제 생성 apply가 가능합니다.
- `itemTemplates`, `skills`, `dropTables`, `dropTableItems` 생성 apply는 계속 잠금 상태입니다.
- `bosses` 생성 row 삭제/복원 allow-list를 추가했습니다.
- `bosses` 삭제 preview에서 `dropTables.owner_type=boss + owner_code` 연결을 검사해 사용 중인 보스는 삭제를 차단합니다.
- 관리자 생성 준비 UI 안내 문구를 새 allow-list에 맞춰 갱신했습니다.
- DB reset / seed는 필요 없습니다.

## v175 - Create Apply FieldZones

- 신규 row 생성 apply 제한 도메인에 `fieldZones`를 추가했습니다.
- `characters`, `enhancementGroups`, `fieldZones`만 실제 생성 apply가 가능합니다.
- `itemTemplates`, `skills`, `dropTables`, `dropTableItems` 생성 apply는 계속 잠금 상태입니다.
- `fieldZones` 생성 row 삭제/복원 allow-list를 추가했습니다.
- `fieldZones` 삭제 preview에서 `dropTables.owner_type=field + owner_code` 연결을 검사해 사용 중인 필드는 삭제를 차단합니다.
- 관리자 생성 준비 UI 안내 문구를 새 allow-list에 맞춰 갱신했습니다.
- DB reset / seed는 필요 없습니다.

## v174 - Admin Collapsed Panel Style Fix

- 접힌 섹션 스타일을 `.section`, `.filter-panel`, `.field-help-panel` 모두에서 통일했습니다.
- `필드 용어 도움말`, `신규 row 생성 준비` 같은 filter/help 기반 탭이 접혔을 때 내부 header만 색칠되던 문제를 수정했습니다.
- 접힌 filter/help 패널은 padding을 제거하고 header가 전체 너비를 차지하도록 보정했습니다.
- `getAdminLayoutShellReadiness()`에 `collapsedPanelStyleReady` 상태를 추가했습니다.
- 기존 관리자 기능과 DB schema는 변경하지 않았습니다.
- DB reset / seed는 필요 없습니다.

## v172 - Admin Layout Navigation Shell

- 관리자 페이지에 sidebar navigation shell을 추가했습니다.
- 상단 header를 sticky 형태로 정리했습니다.
- 주요 섹션에 접기/펼치기 버튼을 추가했습니다.
- 접힌 섹션 상태는 브라우저 localStorage에 저장합니다.
- footer를 현재 버전/상태 표시 영역으로 정리했습니다.
- 기존 edit/create/delete/restore API 기능은 변경하지 않았습니다.
- DB reset / seed는 필요 없습니다.


## v168 - Admin Create Delete Rollback

- `create-apply`로 만든 제한 도메인 row 삭제 되돌리기 preview/apply API를 추가했습니다.
- 대상은 `characters`, `enhancementGroups`의 `action=create` 이력으로 제한했습니다.
- 삭제 preview에서 현재값이 생성 당시 값과 같은지 검사합니다.
- 삭제 preview에서 연결 데이터 blocker 수를 `dependencyBlockerCount`로 표시합니다.
- 연결 데이터가 하나라도 있으면 삭제를 차단합니다.
- 실제 삭제는 dev key와 `DELETE CREATED MASTER DATA ROW` 확인 문구가 필요합니다.
- 삭제 성공 시 `admin_change_logs`에 `action=create_delete`로 기록합니다.
- DB reset / seed는 필요 없습니다.

## v162 - Admin Create Draft Preview

- 신규 row 생성 준비 화면에 blueprint 기반 생성 초안 입력 UI를 추가했습니다.
- 생성 초안은 boolean/select/number/textarea/relation select 타입으로 입력합니다.
- relation select 후보 검색과 owner_type → owner_code 연동 갱신을 지원합니다.
- `POST /api/v1/admin/master-data/create-preview` preview-only API를 추가했습니다.
- code unique 중복, relation 대상 존재, combo guard 중복을 백엔드에서 검증합니다.
- 실제 DB insert, commit, change log, rollback은 아직 잠금 상태입니다.
- DB reset / seed는 필요 없습니다.

## v159 - Admin Create Blueprint Read-only

- 관리자 신규 row 생성 준비용 read-only blueprint API를 추가했습니다.
- 관리자 페이지에 신규 row 생성 준비 섹션을 추가했습니다.
- 도메인별 필수 필드, unique 필드, combo guard, 기본값 draft JSON을 표시합니다.
- relation 필드는 대상 후보 개수를 보여주지만 실제 insert는 아직 잠금 상태입니다.
- JSON 필드는 생성 적용 전까지 잠금으로 표시합니다.
- 기존 edit apply, rollback, change log, localStorage 저장 구조는 유지합니다.
- DB reset / seed는 필요 없습니다.

## v156 - Admin Change Log Relation Tools

- 변경 이력 목록에 relation 변경 개수 배지를 추가했습니다.
- 변경 이력 상세 before/after 값에 relation 대상 이름 label을 표시합니다.
- 변경 이력 상세 relation 값에서 대상 열기 버튼을 사용할 수 있습니다.
- rollback preview의 되돌릴 값 표에서 relation label과 대상 열기 버튼을 표시합니다.
- rollback 현재값 안전 검사 표에서도 relation label을 표시합니다.
- 백엔드 change log detail / rollback preview 응답에 relation metadata를 추가했습니다.
- 기존 rollback guard, dev key, 확인 문구, localStorage 저장 구조는 유지합니다.
- DB reset / seed는 필요 없습니다.

## v153 - Admin Relation Preview Tools

- 변경 preview와 초안 before/after 표에서 relation 값에 대상 이름 label을 함께 표시합니다.
- relation 변경 행에 `relation` 배지를 표시합니다.
- 변경 요약 배너에 relation 변경 개수 표시를 추가했습니다.
- relation 대상이 열 수 있는 도메인이면 `대상 열기` 버튼을 표시합니다.
- `대상 열기`는 code로 카탈로그를 조회한 뒤 해당 상세를 엽니다.
- 기존 preview/apply 백엔드 검증, dev key, 확인 문구, high risk 추가 확인, stale guard는 유지합니다.
- DB reset / seed는 필요 없습니다.

## v150 - Admin Relation Search Tools

- 관계 필드 relation select 검색 input을 추가했습니다.
- 검색은 프론트 UI 안에서만 후보 목록을 좁히며 DB를 수정하지 않습니다.
- 검색 결과가 현재 선택값을 숨기더라도 현재 선택값은 유지되게 했습니다.
- owner_type 변경 시 owner_code 후보 목록과 검색 상태가 같이 안전하게 갱신됩니다.
- 마스터 데이터 카탈로그 검색/페이지 입력에서 Enter 조회를 지원합니다.
- 카탈로그 domain, 표시 개수, 활성 상태, 정렬 변경 시 페이지를 1로 되돌립니다.
- DB reset / seed는 필요 없습니다.

## v147 - Admin Owner Code Relation Tools

- `dropTables.owner_code`를 relation select 기반으로 안전하게 편집할 수 있게 했습니다.
- `owner_type=boss`이면 bosses 목록, `owner_type=field`이면 fieldZones 목록에서만 owner_code를 선택합니다.
- `owner_type`을 바꾸면 `owner_code` 후보 목록도 자동으로 보스/필드 목록으로 전환됩니다.
- preview/apply 공통으로 `owner_type + owner_code` 대상 존재 여부를 백엔드에서 다시 검사합니다.
- 초안 검증 결과에서 relation target label을 함께 표시합니다.
- 기존 dev key, 확인 문구, high risk 추가 확인, stale guard, change log/rollback을 유지합니다.
- DB reset / seed는 필요 없습니다.

## v144 - Admin Combo Relation Guard

- `dropTableItems.drop_table_code` relation select 편집 추가.
- `skillLevels.skill_code`, `skillLevels.level` 편집 추가.
- `enhancementLevels.group_code`, `enhancementLevels.from_level` 편집 추가.
- `characterSkills.character_code`, `characterSkills.skill_code` 편집 추가.
- preview/apply 공통으로 관계 대상 존재 여부 검증.
- `skill_code + level`, `group_code + from_level`, `character_code + skill_code` 중복 조합 검증 추가.
- 관리자 UI relation note에 중복 조합 검사 항목 표시.
- DB reset / seed는 필요 없음.

## v141 - Admin Relation Safe Edit

- 관리자 편집 초안에 relation select 타입을 추가했습니다.
- `itemTemplates.enhance_group_code`를 enhancementGroups 목록 기반 select로 편집할 수 있게 했습니다.
- `dropTableItems.item_template_code`를 itemTemplates 목록 기반 select로 편집할 수 있게 했습니다.
- `dropTables.owner_type`을 boss/field select로 편집할 수 있게 했습니다.
- 백엔드 preview/apply 공통 검증에서 관계 대상 존재 여부를 다시 검사합니다.
- 관계 필드 변경은 high risk/medium risk 안내와 기존 확인 문구, stale guard, change log를 그대로 거칩니다.
- DB reset / seed는 필요 없습니다.

## v138 - Admin Safe Apply Review

- 관리자 편집 초안 아래에 적용 직전 비교 UI를 추가했습니다.
- 실제로 바뀐 필드만 before/after 형태로 보여줍니다.
- 변경 필드를 risk high / medium / low 순으로 정렬해 위험한 변경을 먼저 보이게 했습니다.
- high risk 변경이 있으면 기존 확인 문구 외에 `HIGH RISK EDIT` 추가 확인 문구를 요구합니다.
- 초안 검증 결과의 변경 표에도 위험도 컬럼을 추가했습니다.
- 마스터 데이터 카탈로그에서 현재 상세로 열어둔 행을 `선택됨` 배지와 강조 배경으로 표시합니다.
- DB reset/seed는 필요 없습니다.

## v135 - Master Catalog Pagination + Slot Labels

- 관리자 마스터 데이터 카탈로그에 페이지네이션을 추가했습니다.
- 기본 표시 개수를 20개로 바꿨습니다.
- 기본 정렬을 ID순으로 바꿨습니다.
- 카탈로그 API에 page/offset/totalPages/hasPrevPage/hasNextPage를 추가했습니다.
- equip_slot 숫자 프리셋 6~14를 인게임 특수 장비 슬롯 이름으로 표시합니다.
- DB reset/seed는 필요 없습니다.

## v134 - Admin Safe Selects + Allow-list Expansion

- 관리자 편집 초안에 preset select 타입을 추가했습니다.
- `itemTemplates.item_type`, `itemTemplates.equip_slot`, `skills.slot_key`를 실제 적용 allow-list에 추가했습니다.
- `item_type`, `equip_slot`, `boss_type`, `slot_key`는 오타 방지를 위해 select 프리셋으로 입력하게 했습니다.
- 현재 DB 값이 프리셋에 없으면 select 맨 위에 현재 DB 값으로 표시하게 했습니다.
- 편집 필드마다 `risk high / medium / low` 배지를 표시했습니다.
- field help / value hint / impact guide에 아이템 분류, 장착 슬롯, 스킬 슬롯 설명을 추가했습니다.
- 관계 필드, JSON 필드, id/code 필드는 계속 잠금 유지했습니다.
- DB reset / seed는 필요 없습니다.

# v133 - Admin Edit Input UI

- 관리자 편집 초안 입력 UI를 필드 타입에 맞게 개선했습니다.
- boolean 필드는 checkbox 대신 true/false select로 표시합니다.
- number 필드는 number input으로 표시합니다.
- description/admin_note는 textarea로 표시합니다.
- allow-list 밖 필드는 입력칸 대신 읽기 전용/잠금 필드 카드로 표시하고 잠금 사유를 보여줍니다.
- 백엔드 API/DB schema/seed/localStorage는 변경하지 않았습니다.
- DB reset / seed는 필요 없습니다.


# v132 - handoff cleanup

- 새 채팅 인수인계용 `NEXT_CHAT_HANDOFF.md` 추가.
- 현재 상태 요약 `docs/current/CURRENT_STATUS.md` 추가.
- 다음 단계 추천 `docs/current/NEXT_STEPS.md` 추가.
- 문서 루트 정리: 자주 보지 않는 기록성 문서를 `docs/archive/stage-notes/`로 이동.
- `tools/run_smoke_core.sh`, `tools/run_smoke_all.sh` 추가.
- 기능 로직 변경 없음. DB reset/seed 필요 없음.


## v131 - Admin Edit Stale Guard

- 관리자 편집 적용 전에 편집 화면을 열었을 때의 기준값과 현재 DB 값이 같은지 검사하는 stale guard를 추가했습니다.
- 프론트 편집 초안 검증/적용 요청에 `baseValues`를 함께 보내고, 백엔드는 현재 DB 값이 달라졌으면 `staleChanges`로 차단합니다.
- 오래된 화면에서 최신 DB 값을 덮어쓰는 실수를 막기 위해 실제 적용에는 `baseValues`가 필요합니다.
- 관리자 화면의 초안 검증 결과에 `stale guard`, `stale count`, `오래된 초안 검사` 표를 추가했습니다.
- DB reset / seed는 필요 없습니다.

## v130 - Admin Write Dev Key Guard

- 관리자 실제 적용/되돌리기 API에 `X-Admin-Dev-Key` 임시 잠금장치를 추가했습니다.
- 관리자 페이지에 `관리자 쓰기 dev key 잠금` 영역을 추가했습니다.
- 읽기/미리보기 API는 그대로 열어두고, DB를 바꾸는 apply/rollback apply만 헤더 검사를 통과해야 합니다.
- DB reset / seed는 필요 없습니다.


## v129 - admin change log filters

- 관리자 변경 이력에 target type, row id, action, changed field, applied, sort 필터를 추가했습니다.
- `GET /api/v1/admin/change-logs`에 `action`, `changedKey`, `applied`, `sort` query를 추가했습니다.
- raw before/after JSON은 계속 숨기고 compact rows + 상세 scalar 변경값만 노출합니다.
- DB reset/seed는 필요 없습니다.

## v128
- 관리자 마스터 데이터 실제 적용 후 선택 항목 상세를 다시 불러오고 `/api/v1/game/master-data` 응답을 자동 비교합니다.
- 변경 이력 되돌리기 성공 후에도 되돌린 대상의 master-data API 반영 상태를 자동 확인합니다.
- 자동 확인 결과에 `contextLabel`과 `autoAfterWrite` 정보를 붙여 수동 확인과 구분할 수 있게 했습니다.
- 이 기능은 진단만 수행하며 DB 추가 수정/localStorage 수정/현재 게임 런타임 수정은 하지 않습니다.
- DB reset/seed는 필요 없습니다.

## v127
- 관리자 상세 화면에 `인게임 master-data API 반영 확인` 진단을 추가했습니다.
- 선택한 마스터 데이터 상세 값이 `/api/v1/game/master-data` 응답에도 같은 값으로 내려오는지 비교합니다.
- DB 적용 후 게임 새로고침 전에 DB → FastAPI master-data 응답까지 반영됐는지 확인할 수 있습니다.
- 이 기능은 조회만 수행하며 DB/localStorage/현재 게임 런타임은 수정하지 않습니다.
- Console helper `verifySelectedMasterDataApi()`를 추가했습니다.
- DB reset/seed는 필요 없습니다.

## v124
- 관리자 페이지에서 수정한 `itemTemplates.stackable` 값을 인게임 신규 획득 장비 겹치기 로직에 연결했습니다.
- master-data adapter가 보스 드랍 아이템에 `stackable`, `templateKey`, `itemTemplateCode` 런타임 필드를 붙입니다.
- 일반 장비 드랍도 `addStackableItemToInventory()`를 통과하게 하여 `stackable=true`인 같은 +0 아이템은 count로 겹칩니다.
- 기존 세이브 전체를 자동 병합하지는 않지만, 새 stackable 드랍이 기존 같은 +0 아이템과 만나면 그 슬롯에 겹치고 stackable 값을 보강합니다.
- 겹쳐진 일반 장비를 강화할 때 스택 전체가 강화되지 않도록 1개만 분리해서 강화합니다.
- 인벤토리/보관함/휴지통 슬롯 배지에서 일반 장비도 `count > 1`이면 `xN`을 표시합니다.
- DB reset/seed는 필요 없습니다.

## v122
- 관리자 편집 초안에서 allow-list 필드만 실제 DB 적용할 수 있는 guarded apply를 추가했습니다.
- 새 API `POST /api/v1/admin/master-data/edit-apply`를 추가했습니다.
- 실제 적용에는 확인 문구 `APPLY MASTER DATA EDIT`가 필요합니다.
- 적용 성공 시 `admin_change_logs`에 before/after/rollback 정보를 저장합니다.
- 새 API `GET /api/v1/admin/change-logs`와 관리자 페이지 변경 이력 표를 추가했습니다.
- code, *_code, *_id, *_json, 이미지/asset, 관계 필드는 계속 잠금 상태입니다.
- DB reset/seed는 필요 없습니다.

## v121
- 관리자 페이지의 `grade` 설명을 현재 DB 구조에 맞게 수정했습니다.
- 현재 `itemTemplates.grade`는 normal/rare/epic 희귀도명이 아니라 기존 JS `item.tier`를 옮긴 숫자형 진행 등급입니다.
- 카탈로그/상세/편집 초안에 실제 값 해석 힌트를 추가했습니다. 예: `grade=12` → `tier 12`.
- `enhance_group_code`와 `admin_note`도 값에 따라 간단한 해석 힌트를 표시합니다.
- Console helper `getAdminFieldValueHint()`를 추가했습니다.
- DB reset/seed는 필요 없습니다.

## v120
- 관리자 페이지에 `필드 용어 도움말` 섹션을 추가했습니다.
- `grade`, `enhance group code`, `admin note`의 의미를 관리자 화면에서 바로 확인할 수 있게 했습니다.
- 마스터 데이터 카탈로그 표 제목, 상세 필드, 편집 초안 입력칸 옆에 `?` 도움말 배지를 표시합니다.
- Console helper `getAdminFieldHelp()`와 `listAdminFieldHelp()`를 추가했습니다.
- 화면 설명만 추가했으며 DB/localStorage/게임 런타임은 수정하지 않습니다.
- DB reset/seed는 필요 없습니다.

## v119
- 관리자 편집 초안 입력칸을 활성화하고, 값을 바꾼 뒤 백엔드 dry-run 검증을 할 수 있게 했습니다.
- `POST /api/v1/admin/master-data/edit-preview` API를 추가했습니다.
- 편집 초안 검증은 현재 DB 값과 초안 값을 비교해 변경될 값/오류/변경 없음 항목을 반환합니다.
- `id`, `created_at`, `updated_at`, JSON 필드, 이미지/아이콘 asset 필드는 수정 불가로 검증합니다.
- 실제 DB 저장 버튼은 계속 disabled이며, DB reset/seed는 필요 없습니다.

## v118
- 관리자 마스터 데이터 상세 화면에 `관리자 편집 초안` 잠금 폼을 추가했습니다.
- 선택한 항목의 일반 필드를 disabled 입력칸으로 보여주며, 저장/되돌리기 버튼은 아직 잠금 상태입니다.
- `getAdminEditDraftReadiness()` Console 헬퍼를 추가해 편집 초안이 읽기 전용으로 잠겨 있는지 확인할 수 있습니다.
- 관리자 페이지 상단에 섹션 바로가기 nav를 추가했습니다.
- 문서가 너무 쌓이지 않도록 기록성 MD 파일을 `docs/archive/stage-notes/`로 이동하고 `docs/README.md` 문서 인덱스를 추가했습니다.
- DB reset/seed는 필요 없습니다.

## v117
- 관리자 마스터 데이터 상세 화면에 실제 연결 항목 조회를 추가했습니다.
- `GET /api/v1/admin/master-data/relations` API를 추가했습니다.
- 아이템/스킬/보스/필드/드랍/강화 데이터의 연결 행을 축약된 읽기 전용 목록으로 확인할 수 있습니다.
- 연결 항목의 `보기` 버튼으로 관련 마스터 데이터 상세로 이동할 수 있습니다.
- 원본 JSON과 이미지 data URL은 계속 숨기며, 관리자 쓰기 UI도 계속 차단합니다.
- DB reset/seed는 필요 없습니다.

## v113
- 관리자 페이지 주소 안내를 고정 `5500` 포트가 아니라 현재 게임이 열린 주소 기준으로 계산하도록 수정했습니다.
- `SAVE DATA → admin` overview 모달에 실제 관리자 페이지 URL 표시와 `주소 복사` 버튼을 추가했습니다.
- `admin.html` 상단에 현재 관리자 페이지 주소를 표시하고 복사할 수 있게 했습니다.
- 관리자 페이지의 `게임으로 돌아가기` 링크도 같은 host/port 기준 `index.html`로 보정합니다.
- DB reset/seed는 필요 없습니다.

## v111
- 관리자 페이지 준비를 위해 읽기 전용 `/api/v1/admin/overview` API를 추가했습니다.
- 최근 세이브 스냅샷 요약을 조회하는 `/api/v1/admin/save-snapshots` API를 추가했습니다.
- 관리자 조회 API는 `snapshot_json` 원본을 내려주지 않고 요약/카운트만 반환합니다.
- 브라우저에서 `openAdminReadOnlyOverviewModal()`로 관리자 준비 overview 모달을 열 수 있게 했습니다.
- SAVE DATA 개발 배지에 `admin` 버튼을 추가했습니다. 이 버튼은 조회 전용이며 localStorage/DB를 수정하지 않습니다.
- DB reset/seed는 필요 없습니다.

## v108
- DB 세이브/백업 복구 직후 새로고침할 때 `beforeunload` 자동 저장이 기존 런타임 상태를 다시 localStorage에 덮어쓰는 문제를 수정했습니다.
- 복구 성공 시 `pending_reload` 잠금을 남겨서 새로고침 전 자동저장/수동저장이 복구된 localStorage 값을 덮어쓰지 못하게 했습니다.
- 새로고침 후 게임이 복구된 세이브를 읽으면 잠금을 해제하고 상태를 `applied_after_reload`로 기록합니다.

## v106
- 백엔드 DB 세이브를 localStorage에 덮어쓰기 전에 미리보기 모달로 비교할 수 있게 했습니다.
- 복구 실행 전 현재 localStorage 세이브를 자동 백업합니다.
- 복구 후 바로 런타임에 적용하지 않고 새로고침 후 적용되도록 했습니다.

## v105
- 백엔드 DB 세이브를 실제 게임에 적용하기 전에 localStorage 세이브와 비교하는 preview/compare 브릿지를 추가했습니다.
- `previewBackendSaveSnapshot()`으로 레벨, 골드, 필드, 인벤토리/창고/우편/장착 슬롯 차이를 확인할 수 있습니다.
- 이 단계에서는 DB 세이브를 localStorage나 게임 상태에 덮어쓰지 않습니다.

## v104
- MD/SAVE dev badge 위치를 하단 HUD 바로 위로 올리고, 접힌 상태에서는 우측 상단에 show 버튼이 가지런히 붙도록 조정했습니다.
- SAVE DATA 배지 버튼 행이 줄바꿈되지 않도록 폭과 레이아웃을 조정했습니다.

# 변경 기록

## v186 - Admin change log split contract

- `change logs` 실제 분리 전에 API/window/DOM 계약을 먼저 고정했습니다.
- `getAdminChangeLogSplitContractReadiness()`와 `renderAdminChangeLogSplitContractReadiness()`를 추가했습니다.
- 관리자 JS 분리 준비 카드에서 change logs 계약 상태를 같이 볼 수 있게 했습니다.
- `tools/smoke/frontend/smoke_admin_change_log_split_contract.js`를 추가하고 core smoke에 포함했습니다.
- 실제 JS 파일 분리는 아직 하지 않았고, DB schema/reset/seed 변경은 없습니다.


## v103 - 개발자 배지 하단 HUD 위 배치

- `MASTER DATA`와 `SAVE DATA` 개발자 배지를 하단 HUD 내부가 아니라 하단 인터페이스 바로 위쪽에 고정 배치했습니다.
- 데스크톱에서는 오른쪽 스킬칸 위에 두 배지가 나란히 보이도록 정렬했습니다.
- 좁은 화면에서는 두 배지가 겹치지 않도록 세로로 분리되게 했습니다.
- 배지 위치만 변경했으며 master-data/save-data 로직은 변경하지 않았습니다.

## v101 - SAVE DATA 개발자 배지

- 수동 저장의 백엔드 DB 동기화 상태를 화면에서 확인하는 `SAVE DATA` 개발자 배지를 추가했습니다.
- 배지에서 즉시 `sync`, `load`, `dual`, `local` 작업을 실행할 수 있습니다.
- 저장 정책/상태 변경 시 배지가 즉시 갱신되도록 `upgrade-rpg:backend-save-sync-*` 이벤트를 추가했습니다.
- 백엔드 저장값 `load`는 아직 게임 상태에 적용하지 않고 조회만 합니다.



## v098 - Master-data dev badge toggle alignment

- `hide/show` 토글 버튼 문구를 `hide MD` / `show MD`로 명확하게 바꿨습니다.
- 토글 버튼을 MASTER DATA 배지 상단 정가운데 탭처럼 배치했습니다.
- 배지를 숨겨도 같은 위치에 `show MD` 탭이 남아, Console 없이 화면에서 다시 펼칠 수 있습니다.
- 토글과 배지를 하나의 wrapper 안에서 함께 배치해 버튼이 위로 뜨거나 겹치는 현상을 줄였습니다.


## v095 - Backend master-data dev badge

- 브라우저 화면 하단에 master-data 상태 확인용 개발자 배지를 추가했다.
- 배지는 `file://`, `localhost`, `127.0.0.1` 환경에서 기본 표시된다.
- `applied`, `static_js_mode`, `failed_fallback_to_static_js` 같은 runtime state와 mode/assets/counts 요약을 표시한다.
- Console 헬퍼 `refreshBackendMasterDataDevBadge()`, `showBackendMasterDataDevBadge()`, `hideBackendMasterDataDevBadge()`, `toggleBackendMasterDataDevBadge()`를 추가했다.

## v087 - Preserve nullable skill proc rate

- Preserved missing skill `baseProcRate` values as database `NULL` instead of converting them to `0`.
- Updated `skills.proc_rate` to be nullable in SQLAlchemy and schema draft.
- Added documentation and a smoke test for nullable master-data fields.
- Intended to make `check_master_data_parity.py` pass for `lightsabre.procRate`.


## v086 - Master Data Parity Checker

- `backend/scripts/check_master_data_parity.py`를 추가했습니다.
- 현재 JS 마스터 데이터에서 생성된 `backend/seeds/generated/*.json`과 FastAPI `/api/v1/game/master-data` 응답을 비교할 수 있습니다.
- 기본 경량 응답과 `--include-assets` 이미지 포함 응답을 모두 검사할 수 있습니다.
- characters, skills, itemTemplates, bosses, fieldZones, dropTables, dropTableItems, enhancementRules의 개수와 주요 필드를 비교합니다.
- `tools/smoke/game/smoke_master_data_parity_checker.py`와 `docs/archive/stage-notes/MASTER_DATA_PARITY_CHECKER.md`를 추가했습니다.

## v085 - Frontend Master Data Bridge

- `src/api/game-api-client.js`와 `src/api/master-data-bridge.js`를 추가했습니다.
- 기존 게임 동작은 유지하면서 브라우저 콘솔에서 FastAPI master-data API를 읽어올 수 있게 했습니다.
- `checkBackendMasterData()`, `loadBackendMasterData()`, `getCachedBackendMasterData()` 전역 함수를 추가했습니다.
- `tools/smoke/game/smoke_frontend_master_data_bridge.js`와 `docs/archive/stage-notes/FRONTEND_MASTER_DATA_BRIDGE.md`를 추가했습니다.

## v084 - Master Data Nested Asset Cleanup

- 기본 master-data 응답에서 최상위 asset 필드뿐 아니라 중첩 JSON 내부의 긴 `data:image/...` 문자열도 제거하도록 정리했습니다.
- `?includeAssets=true` 요청에서는 기존처럼 asset 문자열을 포함합니다.
- `tools/smoke/game/smoke_master_data_nested_asset_cleanup.py`와 관련 문서를 추가했습니다.

## v082 - Seed Import Long Asset URL Fix

- `item_templates.icon_url`에 SVG `data:image` 문자열이 500자를 넘어 seed import가 실패하던 문제를 수정했습니다.
- `characters.image_url`, `skills.icon_url`, `item_templates.icon_url`, `bosses.image_url` 컬럼을 `Text` 타입으로 변경했습니다.
- `backend/sql/schema_draft.sql`의 이미지/아이콘 URL 컬럼도 `TEXT`로 맞췄습니다.
- `backend/scripts/setup_dev_db.py`의 SQL 로그 출력을 기본 비활성화했습니다. 긴 seed 데이터가 터미널을 가득 채우는 것을 막고, 필요할 때만 `--verbose-sql`로 볼 수 있습니다.
- `tools/smoke/game/smoke_seed_import_long_asset_columns.py`를 추가했습니다.

## v078 - Seed Import Structure

- `backend/scripts/setup_dev_db.py` 추가
  - 로컬 DB reset/schema 생성/seed import/verify 지원
  - `--dry-run`으로 DB 접속 없이 seed JSON 개수 확인 가능
- `docs/archive/stage-notes/SEED_IMPORT.md` 추가
- `tools/smoke/game/smoke_seed_import_structure.py` 추가
- 매우 큰 HP/골드/강화비용을 고려해 DB 초안/모델의 관련 컬럼을 `NUMERIC(40,0)` 계열로 보정
- `user_mailbox_messages` 테이블을 SQL 초안에 보강


## v077 - Backend env fix + seed extractor

- `backend/app/core/config.py`를 수정해 `CORS_ORIGINS`를 JSON 리스트 형식과 쉼표 문자열 형식 모두 처리할 수 있게 했습니다.
- `backend/.env.example`의 `CORS_ORIGINS` 예시를 안전한 JSON 리스트 형식으로 수정했습니다.
- `backend/pyproject.toml` 버전을 `0.1.1`로 올리고 `asyncpg` 의존성을 명시했습니다.
- `tools/extract_seed_data.js`를 추가해 현재 JS 마스터 데이터를 `backend/seeds/generated/*.json`으로 추출할 수 있게 했습니다.
- `tools/smoke/game/smoke_seed_extraction.js`를 추가해 생성된 seed JSON 기본 검증을 할 수 있게 했습니다.
- `backend/seeds/README.md`, `docs/archive/stage-notes/SEED_EXTRACTION.md`를 추가했습니다.
- Docker/FastAPI 로컬 실행 중 실제로 발생한 `CORS_ORIGINS` 파싱 오류와 `asyncpg` 누락 오류 해결법을 문서에 반영했습니다.
- 기존 프론트 게임 동작은 변경하지 않았습니다.

## v074 - 5순위: API 응답 형태 확정

- `docs/contracts/API_RESPONSE_CONTRACT.md`를 추가해 FastAPI 응답 표준 봉투를 확정했습니다.
- `src/api/api-response-contract.js`를 추가해 응답 버전, 행동 타입, 에러 코드, 응답 생성 헬퍼를 정리했습니다.
- `src/api/API_PLAN.md`를 확정 응답 형태 기준으로 갱신했습니다.
- 저장/불러오기, 마스터 데이터, 전투, 처치/드랍, 장착/해제/강화, 스킬강화권, 보스 소환, 관리자 변경 응답 예시를 정리했습니다.
- 실패 응답 형태와 공통 에러 코드를 정리했습니다.
- `tools/smoke/frontend/smoke_api_response_contract.js`를 추가해 응답 계약 헬퍼와 예시 응답을 자동 검증할 수 있게 했습니다.
- 현재 게임 동작에 영향을 주는 파일은 변경하지 않았습니다. 따라서 브라우저 확인 항목은 없습니다.

## v073 - 4순위 3차: 장착/해제/스킬강화권/보스소환 결과 객체화

- `actionEquipDirect()`에 `item.equip` / `skill_book.use` 결과 객체를 도입했습니다.
- `actionUnequipDirect()`에 `item.unequip` 결과 객체를 도입했습니다.
- `summonBoss()`에 `boss.summon` 결과 객체를 도입했습니다.
- `applyActionResultUi()`가 보스 패널 닫기, 특수보스 패널 닫기, 자동공격 시작 요청을 처리할 수 있게 확장했습니다.
- 장착/해제/스킬강화권/보스소환 성공·실패 사유를 `data.reason` 또는 상세 데이터로 남기도록 정리했습니다.
- 기존 UI 동작은 유지하면서 FastAPI 응답 구조로 옮기기 쉬운 중간 계층을 확장했습니다.
- `tools/smoke/frontend/smoke_action_results.js`를 추가해 주요 결과 객체 생성 여부를 자동 확인할 수 있게 했습니다.

## v072 - 4순위 2차: 처치/드랍/보상 결과 객체화

- `killEnemy()`에 `combat.kill` 결과 객체를 도입했습니다.
- 보스 처치 시 장비/탈리스만/휘장/스킬강화권 드랍 결과를 `data.drops`, `logs`, `effects`에 모으도록 정리했습니다.
- 최초 장비 보너스 스킬강화권 지급 로직이 선택적으로 Action Result에 기록되도록 개선했습니다.
- 필드 몬스터 처치 시 골드/공격속도/순수공격력 성장 보상을 `data.rewards`에 기록하도록 했습니다.
- `applyActionResultUi()`에 `renderUI` 요청 처리를 추가했습니다.
- 기존 게임 동작은 유지하고, FastAPI 응답 구조로 옮기기 위한 중간 계층만 추가했습니다.
## v195 admin thin entry cleanup

- `admin-page-readonly.js` click action handler map 중앙화.
- window export 등록을 `registerAdminReadOnlyPageExports()`로 묶음.
- 외부 모듈 configure 호출을 `configureAdminExternalModules()`로 묶음.
- `getAdminThinEntryCleanupReadiness()` / `renderAdminThinEntryCleanupReadiness()` 추가.
- `tools/smoke/frontend/smoke_admin_thin_entry_cleanup.js` 추가.

## v238 — Backend admin schema field constraint contract

- Added `admin_schema_field_constraint_contract.py`.
- Frozen required fields, defaults, length/range constraints, and Pydantic normalization behavior for Admin request models.
- Added runtime validation checks for whitespace stripping, alias/name population, and invalid payload rejection.
- Added the new smoke to `tools/run_smoke_core.sh`.
- No route path, response body, DB, or env changes.

## v251 - Shared Diff Preview Integration

- 관리자 Preview API에 연결된 `unifiedDiff` / `rollbackSnapshot` 흐름을 기준으로 ChangeLog의 기존 최상위 필드 변경 계산도 공통 Diff Engine을 사용하도록 통합했습니다.
- 기존 API 응답의 `key`, `label`, `before`, `after` 구조는 그대로 유지했습니다.
- `run_smoke_core.sh` 중간 `exit 0` 때문에 v247~v250 Contract 검사가 실행되지 않던 문제를 수정했습니다.
- 공통 Diff Engine에서 legacy ChangeLog 행으로 안전하게 투영하는 스모크 검사를 추가했습니다.

## v252 - Snapshot-based Rollback Preview Guard

- Rollback Preview의 공통 Snapshot 방향을 `현재/적용 값 -> 되돌릴 값`으로 통일했습니다.
- 성공 Preview의 `acceptedChanges`가 없고 기존 ChangeLog `changes`만 남는 차단 상황에서도 Snapshot 방향이 뒤집히지 않도록 보정했습니다.
- 백엔드에 Snapshot schema/fingerprint 무결성 검사를 추가하고, 손상된 Snapshot restore payload 사용을 차단했습니다.
- 관리자 UI에 전체 fingerprint, Snapshot 기준값, 공통 Diff와 Snapshot의 일치 여부를 표시했습니다.
- 새 route, 새 Contract, DB/env/seed/auth/write 로직, 기존 API 응답 필드는 변경하지 않았습니다.
- 전용 Backend/Frontend Smoke를 추가했습니다.

## v253 - Admin Preview Diff 공통 렌더러 통합

- `src/api/admin/admin-preview-diff.js`를 추가해 Create/Edit/ChangeLog/Rollback Preview의 Unified Diff 및 Rollback Snapshot 표시를 공통화했습니다.
- Snapshot schema/fingerprint 형식과 Unified Diff 일치 검사를 공통 모듈 한 곳에서 수행합니다.
- 기존 각 관리자 모듈의 `renderUnifiedPreviewDiff()` 함수 이름과 호출 구조는 유지하고 공통 렌더러로 위임하도록 변경했습니다.
- 기존 route, API 응답 body, DB/env/seed/auth, Write Guard 및 실제 write 로직은 변경하지 않았습니다.
- `smoke_admin_rollback_snapshot_preview.js`를 공통 렌더러 실행·로드 순서·중복 제거까지 확인하도록 강화했습니다.

## v254 admin preview result summary shared renderer

- Added a shared Preview result summary renderer for status banners, metrics, badges, warnings, and notes.
- Connected create, edit, rollback, create-delete, and create-delete-restore Preview result screens to the shared summary renderer.
- Preserved existing API response bodies, routes, DB/env/seed/auth settings, write guards, and write behavior.
- Added frontend smoke coverage for the shared result summary and kept the existing shared Diff/Snapshot renderer unchanged.

## v255 - Admin Preview browser verification

- 관리자 페이지에 API/DB를 호출하지 않는 읽기 전용 Preview 화면 점검 섹션을 추가했습니다.
- 정상 Create, 오류 Create, 정상 Edit, stale Edit, 정상 Rollback, Snapshot 불일치, 삭제 dependency 차단, 복원 ID/code 충돌의 8개 fixture를 제공합니다.
- 모든 예시는 공통 Preview 결과 요약/Diff 렌더러를 사용하며 실제 write 로직과 분리되어 있습니다.
- 전용 smoke에서 API 호출 0회, write 작업 0회, 스크립트 로드 순서와 8개 시나리오 등록을 검사합니다.
## v267.next-chat-handoff-ready

- 다음 채팅에서 바로 이어갈 수 있도록 root/docs handoff prompt를 최신 v266 기준으로 정리했습니다.
- 오래된 v250/v260 중심 인계 문구를 v267/Vue-FastAPI-DB 전환 방향으로 갱신했습니다.
- `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`를 추가했습니다.
- `docs/current/CURRENT_STATUS.md`, `docs/current/ROADMAP.md`, `docs/current/NEXT_STEPS.md`, `README.md`, `docs/archive/production-deployment/BACKEND_READY_V320.md`를 최신 방향에 맞게 정리했습니다.
- 런타임 코드, DB, env, seed, 인증, route, API 응답 body, Write Guard, 실제 write 로직은 변경하지 않았습니다.

## v271.vue-readonly-api-client

- Added Vue read-only API client preparation files under `frontend/vue-app/src/api/`.
- Added GET-only route constants for admin/game/health read APIs.
- Added `requestReadOnly` fetch wrapper without write methods.
- Updated AdminShell/GameShell to display prepared GET route lists without auto-calling APIs.
- Added Vue read-only API smoke coverage.
- Updated current docs, handoff docs, and next-step guidance for v272.
- Did not change DB/env/seed/auth/API response body/route paths/write logic/Write Guard/Preview Apply bodies/game content.

## v270.vue-app-basic-shell

- `frontend/vue-app/`에 Vite + Vue 기본 shell을 추가했습니다.
- `/game`, `/admin` Vue route를 만들었지만 기존 `index.html`, `admin.html`을 대체하지 않았습니다.
- `GameShell.vue`, `AdminShell.vue`, `ShellCard.vue`, 기본 CSS를 추가했습니다.
- Vue shell 구조 검사용 smoke와 실행 스크립트를 추가했습니다.
- 사용자가 직접 해야 할 설치 단계 `frontend/vue-app` 폴더의 `npm install`을 문서화했습니다.
- DB/env/seed/auth/route/API body/Write Guard/실제 write 로직/Preview Apply 요청 body/기존 smoke 의미는 변경하지 않았습니다.
## v273.local-dev-cors-vue-fix

- Fixed the local Vue dev server CORS issue reported from `http://127.0.0.1:5173` to `http://127.0.0.1:8000/api/v1/*`.
- Added local/debug fallback CORS origins in `backend/app/core/config.py` so older local `.env` values that omit Vite port `5173` do not block read-only Vue API checks.
- Production CORS behavior remains explicit: production/debug-false settings do not auto-append local dev origins.
- Added `tools/smoke/backend/smoke_backend_local_cors.py` and included it in `tools/run_smoke_core.sh`.
- Added `docs/current/LOCAL_DEV_CORS.md`.
- Did not change `.env`, DB, seed, auth, route paths, API response body, write logic, Write Guard, Preview/Apply request bodies, or game content.
# v327.third-owner-only-attempt-recorded-vulnerability-gated

- 기호가 preparation `b35dfacf427162b348a6bd29eb030778edc7741c`을 승인한 뒤 lifecycle-only authorization `04e002060e576f19f4d8687b33635a414486206d`으로 run `29883012957`을 정확히 한 번 dispatch.
- 접수 직후 closure `64e5ae0f5e5385ba00df16bb10ac33789ca3760a`으로 gate를 닫고 rerun하지 않음.
- validation, repository checks, local linux/amd64 image build, SPDX SBOM은 성공했으나 Trivy HIGH/CRITICAL 27건으로 publish 차단.
- artifact `8515504259`에 SBOM/vulnerability report 보존. publish job은 skipped되어 GHCR login/push/provenance/Cosign과 registry mutation 없음.
- evidence commit `303a2ed01c69c29894efdcde4ead6c2291c3d8bc`으로 `attempt-recorded` 확정. 다음 단계는 `review-recorded-vulnerability-gate-evidence`.
- gate 완화 없이 exact base image/runtime 구성/Python dependency focused fix를 별도 승인 대상으로 남김.
# v341.lifecycle-preparation-closed-focused-correction

- `789599bfe1a26cad5d8b3d80ee6a9613c5e48576` 승인 뒤 사전 검사에서 lifecycle이 이전 `attempt-recorded`라 workflow의 direct preparation-parent 조건을 만족하지 못함을 확인했습니다.
- workflow dispatch나 새 GHCR mutation 없이 중단했습니다.
- run `29909291344` 성공 evidence를 다섯 번째 `attemptHistory`와 `priorAttemptEvidence`로 보존하고 lifecycle을 `preparation-closed`, gate `false`, approval `null`, not-dispatched로 초기화했습니다.
- static/handoff checker와 정책 JSON을 같은 history에 맞추고 새 focused preparation SHA 승인을 다시 요구합니다.
