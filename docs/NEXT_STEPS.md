# 다음 추천 단계

## 현재 완료

- 공통 Unified Diff/Snapshot 렌더러
- Snapshot 기반 Rollback Preview 방향 및 무결성 검사
- Create/Edit/Rollback/Delete/Restore Preview 결과 요약 공통 렌더러
- 전체 API 응답 body, route, DB, env, seed, 인증, Write Guard 유지

## 다음 단계

관리자 Preview UI의 실제 브라우저 통합 확인을 진행합니다.

1. Create Preview 성공/차단 화면
2. Edit Preview 정상/stale/validation 차단 화면
3. Rollback Preview snapshot/diff 일치 및 불일치 화면
4. 생성 row 삭제의 dependency blocker 화면
5. 삭제 row 복원의 id/code 충돌 화면

화면 확인에서 문제가 없으면 관리자 기능 안정화 단계를 종료하고 게임 콘텐츠 개발 우선순위를 다시 선정합니다.

## v255 이후 추천 단계

1. 관리자 페이지의 `Preview 화면 읽기 전용 점검`에서 8개 fixture의 배너, 배지, 경고, Diff/Snapshot 표시를 브라우저로 확인합니다.
2. 표시가 정상이라면 실제 DB write 없이 기존 Preview API의 정상/차단 응답을 같은 공통 렌더러에 연결하는 통합 점검을 추가합니다.
3. 관리자 안정화가 끝나면 새 Contract 증설을 멈추고 게임 콘텐츠 개발 우선순위를 확정합니다.
