# Next Steps — v309

## 첫 실행

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_runtime_config_hardening.py --strict --require-health
```

정상 결과:

```txt
runtime-config-hardening-verified-local-runtime-preserved
```

## 결과별 다음 단계

- 정상 결과: production secret/TLS/image/Compose 정적 검증 준비로 이동
- `blocked-or-failed`: `.env`, Docker, DB를 변경하지 말고 전체 출력 검토

## 금지

실제 `.env`, Docker 실행 상태, DB schema/data, Alembic revision/history를 임의 변경하지 않습니다.
