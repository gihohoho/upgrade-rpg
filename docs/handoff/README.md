# Handoff package — v308

## 기준 ZIP

```txt
rpg_v308_runtime_config_hardening_ready.zip
```

## 첫 실행

```bash
python tools/check_runtime_config_hardening.py --strict --require-health
```

v307 live runtime 통과 상태를 유지한 채 explicit pool, engine disposal, production fail-closed guard, non-root Dockerfile, 별도 production Compose 안전 경계를 확인합니다.

실제 `.env`, Docker build/up/down, DB, Alembic history는 별도 승인 전 변경하지 않습니다.
