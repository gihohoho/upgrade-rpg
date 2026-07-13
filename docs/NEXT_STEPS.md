# 다음 추천 단계

## 현재 완료

- 공통 Unified Diff/Snapshot 렌더러
- Snapshot 기반 Rollback Preview 방향 및 무결성 검사
- Create/Edit/Rollback/Delete/Restore Preview 결과 요약 공통 렌더러
- 고정 fixture 기반 Preview 화면 점검 패널
- 실제 Preview API 응답을 공통 렌더러로 표시하는 dryRun 전용 Live 점검 패널
- 전체 API 응답 body, route, DB, env, seed, 인증, Write Guard 유지

## v256 이후 추천 단계

1. 관리자 페이지에서 `Preview 화면 점검`의 fixture 버튼 8개가 정상 표시되는지 확인합니다.
2. 생성 설계/편집 상세/변경 이력 상세를 하나씩 연 뒤 `실제 Preview API 응답 표시 점검` 버튼으로 실제 dryRun 응답이 표시되는지 확인합니다.
3. 확인이 끝나면 관리자 안정화 단계를 종료하고 게임 콘텐츠 개발 우선순위를 확정합니다.
4. 다음 개발 우선순위 후보는 콘텐츠 수치/드랍/보스/장비/스킬 UX 중 하나로 좁히는 것을 추천합니다.
