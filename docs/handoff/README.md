# Handoff package — v303

현재 전달 기준:

```txt
rpg_v303_postgres_restore_rehearsal_stamp_postcheck_recovery.zip
```

첫 작업은 `tools/stamp_postgres_restore_rehearsal_database.py --inspect`로 v302 stamp 이후 상태를 읽기 전용 검증하는 것입니다.
같은 rehearsal stamp 재실행과 원본 source stamp는 금지합니다.
