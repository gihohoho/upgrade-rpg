# Codex Next Chat Start Guide — v315

1. `rpg_v315_codex_ghcr_namespace_handoff_ready.zip`을 Codex 새 채팅에 첨부합니다.
2. 루트 `NEXT_CHAT_PROMPT.md` 내용을 첫 메시지로 보냅니다.
3. Codex가 `AGENTS.md`와 `NEXT_CHAT_HANDOFF.md`를 먼저 읽었는지 확인합니다.
4. `backend`에서 `source .venv/Scripts/activate`로 가상환경을 켭니다.
5. 프로젝트 루트에서 `python tools/check_codex_handoff_readiness.py --strict`를 실행합니다.

덮어쓸 때 기존 PC의 `backend/.env`, `backend/.venv`, `local-backups/`, `local-review-artifacts/`는 ZIP에 없으므로 별도로 보존합니다.
