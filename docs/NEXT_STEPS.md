# Next Steps — v327

1. run `29883012957` artifact의 27개 HIGH/CRITICAL 결과와 SBOM을 검토합니다.
2. newer exact base image digest, runtime multi-stage/minimal 구성, fixed version이 있는 Python dependency 2건의 조정안을 비교합니다.
3. `--ignore-unfixed=false`와 HIGH/CRITICAL gate를 유지한 focused fix 범위를 기호에게 승인받습니다.
4. 승인 뒤에만 새 preparation을 만들고 검증·commit·push한 후 정확한 40자 SHA를 다시 승인받습니다.
5. 별도 승인 뒤 새 A → C → R single-dispatch lifecycle을 진행합니다. 기존 세 run은 rerun하지 않습니다.

현재 lifecycle은 `attempt-recorded`, gate는 `false`입니다. GHCR login/push는 3차 실행에서도 미실행이고 registry mutation은 없습니다. 현재 필요한 설치·extension·추가 권한은 없고 서버 재시작도 불필요합니다.
