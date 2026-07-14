# Handoff package — v304

현재 전달 기준:

```txt
rpg_v304_postgres_source_baseline_stamp_final_guard_ready.zip
```

첫 작업은 `tools/stamp_postgres_source_database.py --inspect`로 원본 source stamp 직전 상태를 읽기 전용 검증하는 것입니다.
원본 source `--execute`와 rehearsal stamp 재실행은 별도 승인 전까지 금지합니다.
