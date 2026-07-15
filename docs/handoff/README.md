# Handoff package — v306

기준 ZIP:

```txt
rpg_v306_postgres_next_revision_readonly_preflight_ready.zip
```

첫 읽기 전용 확인:

```bash
python tools/check_postgres_next_revision_preflight.py --strict
```

기존 baseline stamp는 source와 rehearsal 모두 완료됐으므로 재실행하지 않습니다. v306은 next revision 필요 여부만 판단하며 revision/autogenerate/upgrade/downgrade를 실행하지 않습니다.
