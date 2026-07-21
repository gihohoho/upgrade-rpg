# Next Steps — v324

1. v324 workflow, source/semantic hash, lifecycle, checker, 정책 문서 검증을 완료합니다.
2. 새 preparation commit을 `main`에 push합니다.
3. 새 정확한 40자 bootstrap-fix preparation SHA를 기호에게 제시하고 별도 승인을 받습니다.
4. 승인 직후 GitHub live 설정을 재확인하고 authorization에서 `recheckedAtUtc`만 새 시각으로 갱신합니다.
5. 새 A → C → R 단일 실행 lifecycle을 진행합니다.
6. 모든 검증이 끝난 exact digest만 후보로 기록하고 isolated container 검증은 별도 단계로 진행합니다.

현재 lifecycle은 새 `preparation-closed`, gate는 `false`입니다. 첫 실행 증거는 `priorAttemptEvidence`에 보존됐고 동일 run의 rerun은 금지합니다. 현재 필요한 설치·extension·추가 권한은 없으며 서버 재시작도 불필요합니다. actual token/PAT/credential은 파일·Git·로그·채팅·artifact에 넣지 않습니다.

authorization-open workflow의 core 검증은 정적 checker를 직접 먼저 실행한 뒤 `SKIP_GHCR_HANDOFF_SMOKES=1 bash tools/run_smoke_core.sh`를 사용합니다. closed root 전용 handoff smoke 세 개만 제외되며 앱·백엔드 전체 smoke는 유지됩니다.
