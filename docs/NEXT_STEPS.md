# NEXT STEPS

Snapshot 기반 Rollback Preview 강화까지 완료했습니다.

다음 추천 단계는 **관리자 Preview UI 정리 후 게임 콘텐츠 개발 재개**입니다.

1. Preview UI의 Diff/Snapshot 표를 공통 컴포넌트 형태로 정리
2. Create/Edit/Delete/Restore Preview에서 동일한 표시 규칙 사용
3. 관리자 실제 기능 안정화 완료 문서 정리
4. 이후 신규 게임 콘텐츠 개발 시작

계속 유지할 안전 조건:

- 기존 route path 및 API 응답 기존 필드 유지
- DB/env/seed/auth 변경 금지
- Write Guard 및 실제 write 로직 변경 시 별도 단계 검증
