# Current Documents — v309

- 최신 작업: `v309.runtime-engine-source-binding-inspector-fix`
- PostgreSQL baseline: 완료
- 다음 revision: 현재 불필요
- 현재 단계: runtime engine source-binding inspector 재검증

## 우선 문서

- `CURRENT_STATUS.md`
- `PROJECT_STRUCTURE.md`
- `ROADMAP.md`
- `POSTGRES_RUNTIME_ENGINE_BINDING_INSPECTOR_FIX.md`
- `POSTGRES_DEPLOYMENT_RUNTIME_READINESS.md`
- `POSTGRES_RUNTIME_CONFIG_HARDENING.md`
- `POSTGRES_PRODUCTION_DEPLOYMENT_TEMPLATE.md`

v309는 실제 runtime 설정을 바꾸지 않고, 여러 줄 `create_async_engine(settings.database_url, ...)` 호출을 정확히 인식하도록 검사기만 수정합니다.
