
## v260 note

최신 기준은 v260 admin catalog date/limit/json keys UX입니다. `마스터 데이터 카탈로그`에서 수정 시각은 일자만 보이고 `?` tooltip에서 초 단위 시간을 확인합니다. 표시 개수는 10/30/50/100 중 선택하며 기본 10입니다. JSON 키는 앞 3개 chip + 외 N개로 접고 전체 키는 `?` tooltip에서 확인합니다. DB/env/seed/auth/route/API body/write guard/실제 write 로직은 변경하지 않았습니다.

# 다음 채팅 시작 프롬프트

사용자가 제공한 별도 시작 프롬프트를 그대로 사용하고, 첨부 ZIP `rpg_v250_2_project_reorganized_preview_integration.zip`을 현재 기준으로 삼으세요.

작업 전 `python tools/contracts/sync_admin_contract_registry.py --check`와 핵심 smoke를 먼저 실행하세요.
