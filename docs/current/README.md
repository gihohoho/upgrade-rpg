# current 문서

현재 상태와 다음 전환 계획을 담는 기준 문서 폴더입니다.

먼저 볼 문서:

1. `CURRENT_STATUS.md`
2. `LEGACY_PATH_DEPENDENCIES.md`
3. `PROJECT_STRUCTURE.md`
4. `VUE_FASTAPI_DB_TRANSITION_PLAN.md`
5. `ROADMAP.md`

v269 기준 결론:

- 실제 legacy 파일 대이동은 아직 하지 않습니다.
- `admin.html`, `index.html`, `src/`, `backend/`, `tools/` 기존 경로는 smoke/contract 영향이 큽니다.
- legacy 경로 의존성 자동 목록화 도구를 추가했습니다.
- 새 Vue 앱 위치는 `frontend/vue-app/`로 결정했습니다.
- 다음 단계는 기존 legacy를 건드리지 않고 Vue 기본 shell만 별도로 만드는 것입니다.
