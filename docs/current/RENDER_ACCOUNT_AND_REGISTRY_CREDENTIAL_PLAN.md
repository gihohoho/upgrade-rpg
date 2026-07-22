# Render account and registry credential plan — v338

## 읽기 전용 확인 결과

2026-07-22T15:59:18Z 기준 Render Dashboard를 읽기 전용으로 확인했습니다.

- workspace plan: `Hobby (legacy)`
- payment method: `No card on file`
- billing information: 없음
- 기존 service: 1개, 사용자가 직접 suspend, active 0
- 새 Web Service source: `Existing Image` 지원
- private registry: GitHub Container Registry 지원
- 현재 registry credential: 없음
- service/credential/token/payment/deploy mutation: 없음

sanitized evidence는 `deploy/review/render-account-readiness-v337.json`입니다. workspace ID, 기존 service 이름, 계정 정보, token, credential 값은 기록하지 않습니다.

## 추천 credential

기존 GitHub CLI OAuth token은 Render에 저장하지 않습니다. Render 전용 최소 권한 credential을 새로 사용합니다.

```txt
GitHub token type: Personal access token (classic)
Token note: render-upgrade-rpg-ghcr-read
Expiration: 365 days
Scope: read:packages only
repo/write:packages/delete:packages: off/off/off
Render credential name: upgrade-rpg-ghcr-read
Registry: GitHub
Username: gihohoho
Image: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2
```

GitHub Container Registry는 private image pull에 classic PAT의 `read:packages`를 요구합니다. Render도 private GitHub image credential에 `read:packages`를 요구합니다.

- https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- https://render.com/docs/deploying-an-image

## 승인 범위 실행 결과 — 2026-07-23

기호가 아래 범위를 명시적으로 승인했고 모두 완료했습니다.

1. GitHub `Confirm access` 사용자 완료
2. dedicated classic PAT 생성: `read:packages` only, 만료일 2027-07-23
3. Render `upgrade-rpg-ghcr-read` credential 저장
4. verified exact digest를 입력해 `Connect` 성공
5. Render 서비스 설정 화면 진입 확인

첫 PAT는 브라우저 검사 출력에 값이 노출된 것을 감지해 Render에 저장하지 않고 즉시 GitHub에서 폐기했습니다. 교체 PAT는 값 출력 없이 Render로 직접 전달하고 GitHub의 token 표시 화면을 닫았습니다. 실제 값은 어떤 저장소 문서나 evidence에도 기록하지 않습니다.

sanitized 실행 evidence는 `deploy/review/render-private-ghcr-connect-v338.json`입니다.

이 승인에는 Web Service 최종 생성, initial deploy, 환경변수 주입, DB 생성/write/restore/migration이 포함되지 않습니다. Render `Create Web Service` 또는 `Deploy`는 별도 실행 준비 SHA 승인 전 누르지 않습니다.
