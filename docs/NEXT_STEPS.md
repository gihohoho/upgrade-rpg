# Next Steps

## 현재 완료: v175 create apply fieldZones

`fieldZones` 신규 row 생성 apply를 제한적으로 열었고, 생성 row 삭제/복원 guard도 같은 제한 범위에 맞춰 확장했습니다.

## 다음 추천: v176 bosses create apply 검토

`fieldZones`가 안정적으로 확인되면 다음 후보는 `bosses`입니다. 다만 보스는 드랍 테이블과 런타임 노출 영향이 있어 바로 열기 전에 삭제 dependency guard를 먼저 더 점검하는 것이 안전합니다.

## v176 권장 작업

1. 실제 브라우저에서 `fieldZones` 생성 preview/apply 확인.
2. 생성된 `fieldZones` row 삭제 preview에서 `dropTables.owner_type=field + owner_code` blocker 표시 확인.
3. 삭제/복원 apply까지 정상 동작 확인.
4. 이후 `bosses` create apply 제한 오픈 여부 검토.
5. `bosses` 삭제 dependency guard에 `dropTables.owner_type=boss + owner_code` 검사 명시.
6. 문서 업데이트와 smoke 실행.

## 주의할 점

- `itemTemplates`, `skills`, `dropTables`, `dropTableItems`는 아직 create apply를 바로 열지 않는 것이 안전합니다.
- 이 도메인들은 게임 런타임 영향과 relation 의존도가 커서, 생성 기능을 열기 전에 더 강한 검증과 삭제 dependency guard가 필요합니다.
- 기존 게임 동작, localStorage 저장, DB save snapshot dual write는 반드시 유지해야 합니다.

## v175 DB reset / seed 결과

- DB schema 변경 없음.
- DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

## 그 다음 후보

이후 순서는 아래가 좋습니다.

1. `bosses` create apply 제한 오픈 검토.
2. create/delete/restore UI에서 위험도와 dependency 표시 강화.
3. 관리자 페이지 코드 분리 준비.
4. `admin.html` 내부 script/css가 너무 커지면, 기능별 JS/CSS 파일 분리.

## 아직 미루는 것이 좋은 작업

- Vue 전환.
- 관리자 전체 리디자인.
- 모든 도메인 create apply 일괄 오픈.
- itemTemplates/skills/dropTables/dropTableItems 신규 생성 apply.
