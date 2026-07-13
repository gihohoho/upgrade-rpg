
## v260 note

최신 기준은 v260 admin catalog date/limit/json keys UX입니다. `마스터 데이터 카탈로그`에서 수정 시각은 일자만 보이고 `?` tooltip에서 초 단위 시간을 확인합니다. 표시 개수는 10/30/50/100 중 선택하며 기본 10입니다. JSON 키는 앞 3개 chip + 외 N개로 접고 전체 키는 `?` tooltip에서 확인합니다. DB/env/seed/auth/route/API body/write guard/실제 write 로직은 변경하지 않았습니다.

# 다음 채팅 인계

최신 ZIP은 `rpg_v250_2_project_reorganized_preview_integration.zip`입니다.

현재 관리자 readiness는 `v250.backend-admin-rollback-snapshot`, splitStatus는 `admin-schema-field-constraint-contract-v238`입니다.

이번 정리에서 문서/smoke 폴더를 재배치했고, 백엔드 계약을 기준으로 프론트 계약 배열을 자동 동기화하는 도구를 추가했습니다. Preview API는 기존 응답 필드를 유지하면서 `unifiedDiff`, `rollbackSnapshot` 선택 필드를 추가했고 관리자 UI에 공통 Diff 표를 연결했습니다.

다음 단계는 실제 브라우저 확인 후 기존 change-log diff 중복을 공통 엔진으로 점진적으로 교체하는 작업입니다.
