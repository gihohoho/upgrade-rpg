# Upgrade RPG 다음 Codex 작업 프롬프트 — v332

기호의 Upgrade RPG 프로젝트를 현재 Git `main` 최신 상태에서 이어서 진행합니다. 먼저 `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 읽고 저장소 규칙을 지켜주세요.

기호는 코딩을 거의 모릅니다. 항상 한국어로 쉽게 설명하고, 모든 터미널 명령 바로 위에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적어주세요. 필요한 extension, 권한, 설치가 있으면 요청하고 해결될 때까지 다음 handoff에도 기록하세요. Codex가 변경·검증 뒤 git add/commit/push까지 직접 하며 ZIP과 Git 명령 안내는 제공하지 않습니다. 실행 중인 개발 서버는 재사용하고 필요할 때만 재시작합니다.

검증은 위험도에 맞춰 최소 범위부터 실행하세요. 기본은 변경 영역의 전용 checker/smoke 1회이고 실패할 때만 범위를 넓힙니다. 문서·handoff·상태값·검사 결과 문자열만 바꾼 경우에는 관련 strict checker와 handoff smoke만 실행하며 전체 `bash tools/run_smoke_core.sh`는 실행하지 않습니다. 전체 smoke는 backend 핵심 로직, DB/Alembic, API 계약, 공통 구조, 여러 영역 변경 또는 실제 배포 후보 직전에만 1회 실행하고 단순 문구 수정 뒤 반복하지 않습니다.

```txt
latest: v332.verified-digest-production-reference-static-prepared
strict result: verified-digest-production-reference-static-prepared-runtime-blocked
next safe stage: review-production-reference-and-approve-isolated-pull-validation
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR namespace: gihohoho
backend repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility: private
target platform: linux/amd64
CI credential strategy: github-actions-github-token
publish approval model: owner-only-source-controlled-two-step
source-controlled lifecycle gate: attempt-recorded / publishReviewerGateReady=false
production reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2
run_attempt=1: required
single dispatch: required
immediate closure: required
```

`deploy/github-actions-ghcr-publish-lifecycle.json`은 P `preparation-closed` → A `authorization-open` → C `authorization-closed-awaiting-evidence` → R `attempt-recorded` 상태를 지원합니다. authorization은 승인된 preparation의 직접 자식이고 lifecycle 파일 하나만 바꿉니다. run 접수 즉시 immediate closure로 gate를 닫고, 종료 뒤 별도 evidence commit에서 부모 closure의 정확한 `closureCommitSha`와 실제 결과를 기록합니다. 모든 run은 `run_attempt=1`, single dispatch이고 rerun 금지입니다. 일반 계약 next stage 문자열 `review-recorded-workflow-attempt-evidence`도 유지합니다.

3차 실행 증거:

- preparation: `b35dfacf427162b348a6bd29eb030778edc7741c` (기호 승인·소비 완료)
- authorization: `04e002060e576f19f4d8687b33635a414486206d`
- closure: `64e5ae0f5e5385ba00df16bb10ac33789ca3760a`
- evidence: `303a2ed01c69c29894efdcde4ead6c2291c3d8bc`
- run: `29883012957` / `https://github.com/gihohoho/upgrade-rpg/actions/runs/29883012957` / failure
- validation과 로컬 image build 및 SPDX SBOM은 성공, Trivy HIGH/CRITICAL gate가 27건을 찾아 게시를 차단
- artifact `8515504259`, SHA-256 `6a5dfd4cd96754fd365323c7c6a7d1edf18542b5e5729e44220d7bf21ace4c50`, `sbom.spdx.json`과 `trivy-results.json`, 14일 보존
- publish job skipped: GHCR login/push/provenance/Cosign 미실행, image digest 없음, signature 미검증

4차 실행 증거:

- preparation: `13b15409929d77b4e6209481596e4f4550a22ba5` (기호 승인·소비 완료)
- authorization: `4fb31f51ca0de15d77a73390b5a07e394ffce12a`
- closure: `ddf475c1a2449feb50ef2af1a536e4150cf0ad59`
- evidence: `f945214f2387b6aa191655d3740e18ef862bd6fb`
- run: `29886540317` / `https://github.com/gihohoho/upgrade-rpg/actions/runs/29886540317` / failure
- artifact: `8516735247` / `8516749365`, 14일 보존
- image digest: `sha256:6e4aefad0cdf1767670b7f736477dd9e00f17bf49a03fa471828df6667c41149`, signature 미검증

5차 실행 증거:

- preparation: `36e8720a53ef7ff6a8334de6bc99646998d63fc9` (기호 승인·소비 완료)
- authorization: `26a11356e33c978afa8cd8a4881500fa62cdbc5c`
- closure: `1c4a982b2a35d3d45f59e7d9faefcdecca69e6c5`
- evidence: `1f0340ddfcf3c8a74cf14110d5957627d4c5d38a`
- run: `29909291344` / `https://github.com/gihohoho/upgrade-rpg/actions/runs/29909291344` / success
- artifact: `8525220616` SHA-256 `c08e483754d357f2f7120659cea455e670bc570a5fb0db3eadfbc0b217f1e30e`; `8525254543` SHA-256 `697fbb38e30d9328d65e392da819eb1645cb42be5059ca502c29cd3b9241db65`
- verified digest: `sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2`
- exact-digest Trivy 0건, SLSA v1 provenance/SBOM, Cosign sign/verify 성공

첫 작업은 읽기 전용 v332 검사입니다.

실행 위치: `backend` 폴더
Python `.venv` 상태: 꺼짐
새 설치 여부: 없음

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트
Python `.venv` 상태: `backend/.venv` 켜짐
새 설치 여부: 없음

```bash
python tools/check_github_actions_ghcr_static_plan.py --strict
python tools/check_codex_handoff_readiness.py --strict
```

정상 기대 결과:

```txt
result: verified-digest-production-reference-static-prepared-runtime-blocked
next safe stage: review-production-reference-and-approve-isolated-pull-validation
```

4차 run `29886540317`은 validation/local build/SBOM/local Trivy/GHCR login·push까지 성공해 digest `sha256:6e4aefad0cdf1767670b7f736477dd9e00f17bf49a03fa471828df6667c41149`를 만들었습니다. registry provenance와 SBOM도 존재하지만 workflow가 SLSA v1의 `SLSA.buildDefinition.buildType` 대신 구형 `SLSA.buildType`을 검사해 실패했습니다. exact-digest Trivy와 Cosign은 미실행이므로 digest는 unsigned·미검증이며 배포하지 않습니다. 기존 네 run은 rerun 금지입니다.

v330 focused fix를 사용한 5차 run은 모든 gate와 Cosign sign/verify를 통과했습니다. 현재 lifecycle은 `attempt-recorded`, gate는 `false`이고 다섯 run 모두 rerun 금지입니다. v332에서 verified exact digest를 production reference에 정적으로 고정했지만 pull·container·deploy는 실행하지 않았습니다. 다음에는 isolated pull/validation 범위를 기호가 별도 승인한 뒤만 진행하고 production deploy는 다시 별도 승인받으세요.

콘텐츠·코드·DB 개발은 가능하지만 현재 pinned image는 변경 전 snapshot입니다. 코드나 image 포함 콘텐츠가 바뀌면 최신 배포 전에 새 image build와 공급망 검증이 필요합니다. DB row 변경은 image와 별개지만 호환성 검증이 필요하고, schema 변경은 새 Alembic revision과 배포 순서를 별도 승인·검토합니다. 구체적인 요청 전에는 DB/Alembic/content mutation을 실행하지 마세요.

로컬 확인 시 backend와 Vue는 실행 중이었지만 PostgreSQL `127.0.0.1:55432`가 꺼져 DB API가 500이었고 legacy HTML용 `127.0.0.1:5500` 서버도 꺼져 있었습니다. 이 때문에 `index.html`·`admin.html`에서 `Failed to fetch`가 발생했으며 배포 준비상 정상 표시는 아닙니다.

사용자 별도 요청 전에는 DB/Alembic/auth/API write/Vue Preview·Apply·write/게임 콘텐츠와 밸런스/production Compose·container·network·volume/자동 deploy를 변경하거나 실행하지 마세요. actual secret/token/PAT/credential/CA/cert/key는 Git·채팅·로그·artifact에 넣지 않습니다.
