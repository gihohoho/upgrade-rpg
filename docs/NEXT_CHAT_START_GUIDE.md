# Next Chat Start Guide — v311

1. `NEXT_CHAT_PROMPT.md` 내용을 새 채팅에 붙여넣습니다.
2. `rpg_v311_production_capacity_tls_network_plan_handoff_ready.zip`을 첨부합니다.
3. 기존 프로젝트 폴더에 ZIP을 덮어쓸 때 `backend/.env`, `local-backups/`, `local-review-artifacts/`를 보존합니다.
4. 새 채팅의 첫 명령은 v311 읽기 전용 checker입니다.

```bash
python tools/check_production_capacity_tls_network_plan.py --strict
```

production Compose와 Docker 명령은 실행하지 않습니다.
