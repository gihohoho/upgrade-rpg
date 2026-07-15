# PostgreSQL runtime engine binding inspector fix — v309

## 문제

v308에서 SQLAlchemy pool 옵션을 명시하면서 `create_async_engine()` 호출이 여러 줄로 정리되었습니다. 실제 runtime은 계속 첫 번째 인자로 `settings.database_url`을 사용했지만, v307 readiness 검사기는 아래처럼 한 줄 문자열만 찾았습니다.

```txt
create_async_engine(settings.database_url
```

따라서 정상적인 여러 줄 호출을 `runtime engine bypasses settings.database_url`로 오판했습니다. DB 연결, `.env`, Docker, Alembic 또는 application data 문제는 아니었습니다.

## v309 수정

- Python AST로 `create_async_engine()` 호출을 분석합니다.
- 첫 positional argument 또는 `url=`/`database_url=` keyword가 정확히 `settings.database_url`인지 확인합니다.
- 줄바꿈, 들여쓰기, pool keyword 추가 여부와 무관하게 판정합니다.
- literal URL이나 `settings.audit_database_url` 같은 다른 설정은 허용하지 않습니다.
- 기존 결과 계약 `runtime-config-hardening-verified-local-runtime-preserved`는 유지합니다.

## 안전 경계

이 수정은 정적 검사기와 smoke만 변경합니다.

```txt
DB schema/data 변경: 없음
backend/.env 변경: 없음
Docker 실행/변경: 없음
Alembic revision/stamp/upgrade/downgrade: 없음
FastAPI route/response body 변경: 없음
runtime engine/pool 설정 변경: 없음
```

## 재검증 명령

```bash
python tools/check_runtime_config_hardening.py --strict --require-health
```

정상 결과:

```txt
result: runtime-config-hardening-verified-local-runtime-preserved
next safe stage: separate-production-secrets-tls-and-container-validation
```
