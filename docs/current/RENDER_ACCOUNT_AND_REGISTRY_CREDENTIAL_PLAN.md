# Render account and registry credential plan — v337

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

## 다음 승인 범위

기호가 아래 범위를 명시적으로 승인했습니다. 현재는 GitHub `Confirm access` verification code 사용자 입력을 기다립니다.

1. GitHub에서 위 이름·만료·scope의 dedicated classic PAT 생성
2. token 값을 채팅·파일·로그에 출력하지 않고 Render `upgrade-rpg-ghcr-read` credential에 직접 전달
3. exact-digest image URL을 입력하고 Render `Connect`로 private image pull 접근만 확인
4. token 생성 시각과 만료 예정일을 값 없이 `SECURITY_ROTATION_AND_GITHUB_GATES.md`에 기록

이 승인에는 Web Service 최종 생성, initial deploy, 환경변수 주입, DB 생성/write/restore/migration이 포함되지 않습니다. Render `Create Web Service` 또는 `Deploy`는 별도 실행 준비 SHA 승인 전 누르지 않습니다.
