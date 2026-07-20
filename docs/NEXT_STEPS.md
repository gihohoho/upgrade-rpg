# Next Steps — v322

1. `python tools/check_github_actions_ghcr_static_plan.py --strict`
2. `python tools/check_codex_handoff_readiness.py --strict`
3. 관련 v322 smoke, compileall, JavaScript 문법, `bash tools/run_smoke_core.sh`
4. preparation-fix commit을 `main`에 commit/push
5. 새 정확한 40자 preparation-fix SHA와 변경 범위를 기호에게 제시
6. 기호의 새 SHA 명시 승인 대기; `f4788acf...` 과거 승인 재사용 금지
7. 승인 직후 GitHub live 설정을 다시 확인
8. 승인 SHA의 direct child에서 lifecycle JSON 한 파일만 authorization-open으로 변경
9. `run_attempt=1`과 Actions API single dispatch를 만족하는 workflow를 정확히 한 번 실행
10. run ID 접수 즉시 immediate closure commit으로 gate를 닫아 `authorization-closed-awaiting-evidence`로 전이; C commit의 `closureCommitSha=null`
11. 성공·실패와 digest/partial evidence를 확인해 별도 `attempt-recorded` evidence commit에서 부모 C commit SHA를 `closureCommitSha`에 기록; non-success conclusion만으로 registry mutation/signature 미실행을 단정하지 않고 job/step 증거 확인
12. `review-recorded-workflow-attempt-evidence`에서 실제 conclusion/digest/signature 증거 검토
13. 모든 검증이 끝난 exact digest만 후보로 기록하고 isolated container 검증은 별도 단계로 진행

현재 lifecycle은 `preparation-closed`, gate는 `false`이며 workflow/login/build/push는 미실행입니다. 필요한 설치, extension, 추가 권한은 없습니다. 서버 재시작도 불필요합니다. actual token/PAT/credential은 파일·Git·로그·채팅·artifact에 넣지 않습니다.

authorization-open workflow의 core 검증은 정적 checker를 직접 먼저 실행한 뒤 `SKIP_GHCR_HANDOFF_SMOKES=1 bash tools/run_smoke_core.sh`를 사용합니다. closed root 전용 handoff smoke 세 개만 제외되며 앱·백엔드 전체 smoke는 유지됩니다.
