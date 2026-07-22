# Next Steps — v326

1. run `29877813770`의 recorded evidence와 registry 미변경 사실을 검토합니다.
2. 기호가 승인하면 `backend/Dockerfile.production` bootstrap target 한 곳만 `3`에서 `3.11`로 수정합니다.
3. 새 retry preparation을 검증·commit·push하고 정확한 40자 SHA를 다시 승인받습니다.
4. 승인 직후 GitHub live 설정을 재확인하고 새 A → C → R 단일 실행 lifecycle을 진행합니다.
5. 모든 검증이 끝난 exact digest만 후보로 기록하고 isolated container 검증은 별도 단계로 진행합니다.

현재 lifecycle은 `preparation-closed`, gate는 `false`입니다. 첫·두 번째 실행은 `attemptHistory`에 보존됐고 두 run 모두 rerun 금지입니다. Dockerfile focused fix는 완료됐으며 새 preparation exact SHA 승인 전에는 workflow를 실행하지 않습니다. 현재 필요한 설치·extension·추가 권한은 없고 서버 재시작도 불필요합니다. actual token/PAT/credential은 파일·Git·로그·채팅·artifact에 넣지 않습니다.

authorization-open workflow의 core 검증은 정적 checker를 직접 먼저 실행한 뒤 `SKIP_GHCR_HANDOFF_SMOKES=1 bash tools/run_smoke_core.sh`를 사용합니다. closed root 전용 handoff smoke 세 개만 제외되며 앱·백엔드 전체 smoke는 유지됩니다.
