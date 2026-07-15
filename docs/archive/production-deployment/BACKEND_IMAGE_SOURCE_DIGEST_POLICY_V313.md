# Backend image source and digest policy — v313

## v314 후속 상태

이 문서는 v313에서 선택 전 안전 경계를 만든 기록입니다. 현재 선택값은 `BACKEND_IMAGE_REGISTRY_BASE_SELECTION.md`를 우선합니다.

```txt
registry: GitHub Container Registry (ghcr.io)
repository template: ghcr.io/<github-account-or-organization>/upgrade-rpg-backend
namespace resolved: no
target platform: linux/amd64
base image digest approved: yes
pull/build/push approved: no/no/no
```

## 이번 단계에서 확정한 것

기호 PC에서 v312 Compose config render-only가 정상 통과했습니다. 해당 출력 중 민감정보가 없는 안전 요약만 다음 파일에 기록했습니다.

```txt
deploy/review/production-compose-config-render-v312.json
```

고정된 결과:

```txt
rendered services: backend
host ports/build/named volumes absent: True/True/True
managed DB service absent / backend replicas: True/1
digest/production guard/TLS/edge rendered: True/True/True/True
image pull/build executed: no
container/network/volume mutation executed: no
DB/Alembic mutation executed: no
```

raw Compose render, 실제 env, secret, registry credential은 저장하지 않았습니다.

## production backend image 계약

운영 Compose에서 사용할 backend image는 tag가 아니라 exact digest만 허용합니다.

```txt
production reference mode: digest-only
<approved-registry>/<approved-namespace>/upgrade-rpg-backend@sha256:<approved-64-hex-digest>
```

필수 기록 항목:

- 승인된 registry provider
- namespace와 repository identity
- 빌드한 Git commit 40자리 SHA
- target platform
- base image exact digest
- 생성된 backend image exact digest
- SBOM 결과
- build provenance 결과
- signature verification 결과
- vulnerability review 결과

## 현재 보류된 선택

```txt
registry provider: deferred
repository identity: placeholder only
target platform: deferred
base image digest approved: no
actual backend image digest approved: no
```

현재 Dockerfile의 base image inventory는 다음입니다.

```txt
python:3.11-slim
```

이 값은 mutable tag이므로 production build 승인 조건을 만족하지 않습니다. base image exact digest를 별도 검토하기 전에는 production image build를 실행하지 않습니다. 로컬 Dockerfile을 이번 단계에서 임의 digest로 변경하지 않은 이유는 승인되지 않은 digest를 고정하거나 로컬 개발 동작을 깨뜨리지 않기 위해서입니다.

## 공급망 검증 게이트

release 전에 다음 네 가지가 모두 필요합니다.

```txt
SBOM required: yes
provenance required: yes
signature verification required: yes
vulnerability review required: yes
```

사용할 구체적인 registry·서명·scan 도구는 provider와 배포 환경을 정한 뒤 결정합니다. 실제 도구 설치나 registry 로그인은 이번 단계에 포함하지 않습니다.

## 승인 상태

```txt
config render evidence verified: yes
image pull/build/push approved: no/no/no
image pull/build/push executed: no/no/no
container start approved: no
actual registry credential applied: no
actual image digest applied: no
actual production value applied: no
```

## 다음 안전 단계

```txt
select-registry-repository-platform-and-base-image-digest
```

다음에는 아래 네 항목을 먼저 확정합니다.

1. registry provider
2. repository namespace/name
3. production target platform
4. `python:3.11-slim`에 대응하는 승인된 base image digest

그 후에도 `pull`, `build`, `push`는 각각 분리된 승인 경계로 실행합니다.

## 읽기 전용 검사

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_backend_image_source_digest_policy.py --strict
```

정상 결과 핵심:

```txt
config render evidence verified: True
registry/repository/platform: deferred / <placeholder> / deferred
production reference mode: digest-only
base image digest pinned/approved: False/False
supply-chain gates required: 4/4
image pull/build/push approved: no/no/no
result: backend-image-source-digest-policy-verified-provider-and-build-blocked
next safe stage: select-registry-repository-platform-and-base-image-digest
```
