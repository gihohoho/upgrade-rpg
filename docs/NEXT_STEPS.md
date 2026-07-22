# Next Steps — v328

1. v328 Alpine/musllinux runtime-minimization preparation을 검증·commit·push합니다.
2. 준비 commit의 정확한 40자 SHA를 기호에게 승인받습니다.
3. 승인 뒤 GitHub live 설정을 재확인하고 lifecycle 파일만 바꾸는 authorization commit을 만듭니다.
4. 새 A → C → R single-dispatch lifecycle을 진행합니다. 기존 세 run은 rerun하지 않습니다.
5. 성공한 exact digest만 isolated 검증 후보로 사용합니다.

현재 lifecycle은 `preparation-closed`, gate는 `false`입니다. 로컬 후보는 Trivy HIGH/CRITICAL 0건이지만 GHCR login/push와 registry mutation은 실행하지 않았습니다. 현재 필요한 설치·extension·추가 권한은 없고 서버 재시작도 불필요합니다.
