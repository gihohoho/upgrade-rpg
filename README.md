# Upgrade RPG

현재 안정 버전: v174 admin collapsed panel style fix

관리자 페이지 sidebar, sticky header, section 접기/펼치기, footer를 유지하면서 접힌 탭 스타일을 공통 규칙으로 보정했습니다. 기존 관리자 edit/create/delete/restore 기능은 유지됩니다.

백엔드/관리자 인수인계는 `NEXT_CHAT_HANDOFF.md`, 현재 상태는 `docs/CURRENT_STATUS.md`, 다음 단계는 `docs/NEXT_STEPS.md`를 참고하세요.


## v174 관리자 접힌 탭 스타일 보정

- `filter-panel` / `field-help-panel` 접힘 상태에서도 전체 카드 색상이 통일되도록 수정.
- 필드 용어 도움말, 신규 row 생성 준비, 관리자 쓰기 잠금, 세이브 스냅샷 필터 등 모든 접힘 탭이 같은 스타일로 보이도록 보강.
- 기존 기능/API/DB는 변경 없음.
