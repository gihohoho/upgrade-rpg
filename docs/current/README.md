# current 문서

현재 상태와 다음 전환 계획을 담는 기준 문서 폴더입니다.

먼저 볼 문서:

1. `CURRENT_STATUS.md`
2. `PROJECT_STRUCTURE.md`
3. `VUE_FASTAPI_DB_TRANSITION_PLAN.md`
4. `ROADMAP.md`

v268 기준 결론:

- 실제 legacy 파일 대이동은 아직 하지 않습니다.
- `admin.html`, `index.html`, `src/`, `backend/`, `tools/` 기존 경로는 smoke/contract 영향이 큽니다.
- 다음 단계는 legacy 경로 의존성을 자동 목록화하고, Vue 앱을 기존 구조 옆에 만들 수 있는지 결정하는 것입니다.
