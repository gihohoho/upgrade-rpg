# NEXT STEPS

현재 추천 단계는 **Snapshot 기반 Rollback Preview 강화**입니다.

1. Preview 응답의 `rollbackSnapshot` fingerprint를 관리자 UI에서 전체 확인 가능하게 표시
2. Rollback Preview 요청 시 저장된 snapshot과 현재 대상의 일치 여부를 비교하는 읽기 전용 검증 추가
3. mismatch가 있으면 실제 write 없이 차단 사유와 변경 경로를 UI에 표시
4. 기존 route path, API response body의 기존 필드, Write Guard는 유지

그다음 단계는 게임 콘텐츠 개발 재개입니다.
