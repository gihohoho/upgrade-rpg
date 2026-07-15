# Next Chat Start Guide — v313

1. `NEXT_CHAT_PROMPT.md`를 새 채팅에 붙여넣습니다.
2. `rpg_v313_backend_image_source_digest_policy_handoff_ready.zip`을 첨부합니다.
3. 덮어쓸 때 `backend/.env`, `local-backups/`, `local-review-artifacts/`를 보존합니다.
4. `backend`에서 `source .venv/Scripts/activate`로 가상환경을 켭니다.
5. 프로젝트 루트에서 v313 image policy checker를 실행합니다.

```bash
python tools/check_backend_image_source_digest_policy.py --strict
```

registry/provider/platform/base digest 선택 전까지 pull/build/push/up/down은 실행하지 않습니다.
