# Next Steps — v329

1. run `29886540317`의 provenance/SBOM artifact와 실패 로그를 검토합니다.
2. workflow의 `SLSA.buildType`을 `SLSA.buildDefinition.buildType`으로 바꾸는 focused fix를 별도 승인받습니다.
3. 승인 뒤 새 preparation을 검증·commit·push하고 정확한 40자 SHA를 다시 승인받습니다.
4. 새 A → C → R single-dispatch lifecycle을 진행합니다. 기존 네 run은 rerun하지 않습니다.
5. exact-digest Trivy와 Cosign까지 통과한 digest만 isolated 검증 후보로 사용합니다.

현재 lifecycle은 `attempt-recorded`, gate는 `false`입니다. GHCR digest는 존재하지만 unsigned·미검증이므로 배포하지 않습니다. 현재 필요한 설치·extension·추가 권한은 없고 서버 재시작도 불필요합니다.
