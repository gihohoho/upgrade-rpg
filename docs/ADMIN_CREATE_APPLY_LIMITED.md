# Admin Create Apply Limited

v165에서는 신규 row 생성 기능을 처음으로 아주 제한적으로 열었다.

## 열린 범위

실제 DB insert가 가능한 도메인은 아래 두 개뿐이다.

- `characters`
- `enhancementGroups`

두 도메인은 relation 의존도가 낮아서 신규 row 생성의 첫 적용 범위로 선택했다.

## 적용 조건

신규 row 실제 생성에는 아래 조건이 모두 필요하다.

- 관리자 쓰기 dev key
- 생성 초안 preview 검증 통과
- 정확한 생성 확인 문구 `CREATE MASTER DATA ROW`
- create allow-list 도메인 통과

## 계속 잠긴 범위

아래 도메인은 계속 preview-only다.

- `itemTemplates`
- `skills`
- `skillLevels`
- `bosses`
- `fieldZones`
- `dropTables`
- `dropTableItems`
- `enhancementLevels`
- `characterSkills`

## Change log

생성이 성공하면 `admin_change_logs`에 `action=create`로 기록한다.

현재 create rollback/delete는 일부러 열지 않았다. 생성 이력 상세 조회는 가능하지만 되돌리기 적용은 기존 update rollback과 분리해서 다음 단계에서 설계한다.

## DB reset / seed

필요 없음.

스키마 변경도 없다.
