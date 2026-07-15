# Codex Next Chat Start Guide — v318

1. 현재 프로젝트 폴더와 Git `main` 최신 commit을 사용합니다. ZIP은 첨부하지 않습니다.
2. 필요하면 루트 `NEXT_CHAT_PROMPT.md` 내용을 첫 메시지로 보냅니다.
3. Codex가 `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 먼저 읽었는지 확인합니다.
4. `backend`에서 `source .venv/Scripts/activate`로 가상환경을 켭니다.
5. 프로젝트 루트에서 `python tools/check_github_actions_ghcr_static_plan.py --strict`를 실행합니다.
6. 필요한 extension/권한/설치 요청이 있으면 기호가 승인하거나 연결하고, 해결되지 않으면 다음 작업에서도 다시 확인합니다.
7. 작업 완료 후 Codex가 NEXT_CHAT 문서를 갱신하고 직접 add/commit/push합니다.

실제 `backend/.env`, `backend/.venv`, `local-backups/`, `local-review-artifacts/`는 로컬 전용이며 Git에 추가하지 않습니다.
