# Next Chat Start Guide — v312

1. `NEXT_CHAT_PROMPT.md`를 새 채팅에 붙여넣습니다.
2. `rpg_v312_managed_postgres_reverse_proxy_config_render_ready.zip`을 첨부합니다.
3. 덮어쓸 때 `backend/.env`, `local-backups/`, `local-review-artifacts/`를 보존합니다.
4. `backend`에서 `source .venv/Scripts/activate`로 가상환경을 켭니다.
5. 프로젝트 루트에서 selection checker와 config render-only wrapper를 순서대로 실행합니다.

```bash
python tools/check_production_managed_postgres_reverse_proxy_selection.py --strict
python tools/render_production_compose_config.py --execute --confirm-stage v312-config-render-only
```

pull/build/up/down은 실행하지 않습니다.
