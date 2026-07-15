# Backend image registry and base selection — v314

## 확정한 선택

```txt
registry: GitHub Container Registry (GHCR)
registry host: ghcr.io
repository: upgrade-rpg-backend
repository visibility: private
production target platform: linux/amd64
base image: python:3.11.15-slim-bookworm
base image linux/amd64 manifest digest: sha256:28255a3ace7eb4c48bc1b57b90af29e1bc82b4fd6c60614a8e3dce61b87ff941
```

## GitHub namespace 주의

현재 repository 주소는 아래 template입니다.

```txt
ghcr.io/<github-account-or-organization>/upgrade-rpg-backend
```

`<github-account-or-organization>`에는 **실제로 이 프로젝트 이미지를 소유할 GitHub 사용자 이름 또는 Organization 이름**만 넣습니다. assistant가 이름을 추측하거나 임의로 만들지 않습니다.

현재 상태:

```txt
namespace resolved: no
actual namespace applied: no
```

따라서 placeholder가 남아 있는 동안에는 registry login, image build, image push를 승인하지 않습니다. 실제 namespace가 정해지면 최종 주소는 다음 형태입니다.

```txt
ghcr.io/실제-GitHub-사용자명-또는-조직명/upgrade-rpg-backend
```

## production image reference

운영 Compose는 최종 backend image도 tag가 아니라 exact digest로만 받습니다.

```txt
ghcr.io/<github-account-or-organization>/upgrade-rpg-backend@sha256:<approved-64-hex-digest>
```

여기서 앞의 namespace placeholder와 뒤의 backend image digest는 아직 실제 값이 아닙니다.

## production base image

로컬 개발 호환성을 위해 기존 `backend/Dockerfile`은 `python:3.11-slim` 상태로 보존했습니다. 운영 빌드 전용 파일을 별도로 추가했습니다.

```txt
backend/Dockerfile.production
```

운영 Dockerfile의 첫 줄:

```dockerfile
FROM python:3.11.15-slim-bookworm@sha256:28255a3ace7eb4c48bc1b57b90af29e1bc82b4fd6c60614a8e3dce61b87ff941 AS runtime
```

- `python:3.11.15-slim-bookworm`: 사람이 읽는 고정 tag
- `sha256:28255a3ace7eb4c48bc1b57b90af29e1bc82b4fd6c60614a8e3dce61b87ff941`: `linux/amd64` manifest 고유번호
- `sha256:b18992999dbe963a45a8a4da40ac2b1975be1a776d939d098c647482bcad5cba`: Docker Hub multi-platform index 고유번호

이번 v314에서는 target platform이 `linux/amd64`이므로 운영 Dockerfile은 해당 manifest digest를 직접 고정합니다.

## 승인 상태

```txt
base image digest approved: yes
credential storage decision: deferred
pull/build/push approved: no/no/no
pull/build/push executed: no/no/no
container start approved: no
actual registry credential applied: no
actual Docker/DB/Alembic mutation: no
```

## 다음 안전 단계

```txt
resolve-ghcr-namespace-and-review-credential-storage
```

다음 단계에서는 실제 GitHub 사용자 이름 또는 Organization 이름을 확인하고, credential을 Git에 저장하지 않는 보관 방법만 먼저 결정합니다. 그 후에도 pull/build/push는 각각 별도 승인 경계입니다.

## 읽기 전용 검사

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_backend_image_registry_base_selection.py --strict
```

정상 결과 핵심:

```txt
registry provider/host: github-container-registry / ghcr.io
repository template: ghcr.io/<github-account-or-organization>/upgrade-rpg-backend
namespace resolved: False
target platform: linux/amd64
base image digest approved: True
image pull/build/push approved: no/no/no
result: ghcr-amd64-base-image-selection-verified-namespace-required-pull-build-blocked
next safe stage: resolve-ghcr-namespace-and-review-credential-storage
```
