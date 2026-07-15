# Next Chat Start Guide — v309

## 첨부 ZIP

- `rpg_v309_runtime_engine_source_binding_inspector_fix_ready.zip`

## 시작 명령

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태

```bash
python tools/check_runtime_config_hardening.py --strict --require-health
```

## 주의

- v308 오류는 DB 문제가 아니라 검사기 줄바꿈 오탐
- 실제 DB/.env/Docker mutation 없음
- production Compose는 검토 초안이며 실행 금지
- source/rehearsal stamp 재실행 금지
- 새 revision/autogenerate/upgrade/downgrade 금지
