# Codex Next Chat Start Guide — v321

1. 현재 프로젝트 폴더와 Git `main` 최신 commit을 사용합니다. ZIP은 첨부하지 않습니다.
2. 필요하면 루트 `NEXT_CHAT_PROMPT.md` 내용을 첫 메시지로 보냅니다.
3. Codex가 `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 먼저 읽었는지 확인합니다.
4. 이미 실행 중인 backend `127.0.0.1:8000`, frontend `127.0.0.1:5173`가 정상이면 끄거나 다시 켜지 않고 재사용합니다.
5. `backend`에서 `source .venv/Scripts/activate`로 가상환경을 켭니다.
6. 프로젝트 루트에서 `python tools/check_github_actions_ghcr_static_plan.py --strict`와 `python tools/check_codex_handoff_readiness.py --strict`를 실행합니다.
7. 기호가 선택한 모델은 `owner-only-source-controlled-two-step`이며 dependency/frontend 입력 잠금은 완료됐습니다. 다음 단계는 v321 preparation commit의 정확한 40자 SHA를 기호가 명시 승인하는 것입니다. 승인 뒤 GitHub 설정을 live 재확인하기 전에는 source-controlled gate를 `false`로 유지하고 workflow를 실행하지 않습니다.
8. 필요한 extension/권한/설치 요청이 있으면 기호가 승인하거나 연결하고, 해결되지 않으면 다음 작업에서도 다시 확인합니다.
9. 작업 완료 후 Codex가 NEXT_CHAT 문서를 갱신하고 직접 add/commit/push합니다.

실제 `backend/.env`, `backend/.venv`, `local-backups/`, `local-review-artifacts/`는 로컬 전용이며 Git에 추가하지 않습니다. `.env` 점검 권한은 허용됐지만 secret 노출·커밋은 계속 금지입니다.
