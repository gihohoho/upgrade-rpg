# Upgrade RPG 문서 안내 — v302

현재 작업 기준은 `v302.postgres-restore-rehearsal-stamp-head-guard-ready`입니다.

## 먼저 읽을 문서

```txt
docs/current/CURRENT_STATUS.md
docs/NEXT_STEPS.md
docs/current/POSTGRES_RESTORE_REHEARSAL_STAMP_GUARD.md
docs/NEXT_CHAT_START_GUIDE.md
```

## 핵심 상태

- v301 source baseline stamp preflight 사용자 PC 실제 통과
- v302 restore rehearsal stamp guard 준비 완료
- `--inspect`는 exact target/revision과 application schema/row-content digest를 읽기 전용 확인
- 실제 rehearsal stamp는 별도 승인 전 금지
- 원본 `rpg_game` stamp/upgrade/downgrade는 계속 금지

루트 인수인계 파일과 `docs/handoff/` 사본은 같은 v302 기준으로 유지합니다.
