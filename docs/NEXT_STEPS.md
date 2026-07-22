# Next Steps — v330

1. v330 `SLSA.buildDefinition.buildType` focused fix preparation을 검증·commit·push합니다.
2. 새 preparation의 정확한 40자 SHA를 기호에게 별도 승인받습니다.
3. 승인 후 새 A → C → R single-dispatch lifecycle을 진행합니다. 기존 네 run은 rerun하지 않습니다.
4. exact-digest Trivy와 Cosign까지 통과한 digest만 isolated 검증 후보로 사용합니다.

현재 lifecycle은 `preparation-closed`, gate는 `false`, 승인 SHA는 `null`입니다. GHCR의 기존 digest는 unsigned·미검증이므로 배포하지 않습니다. 현재 필요한 설치·extension·추가 권한은 없고 서버 재시작도 불필요합니다.
