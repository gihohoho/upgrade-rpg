# Admin Create Apply Limited

v165에서는 신규 row 생성 기능을 처음으로 아주 제한적으로 열었다. v175에서는 `fieldZones`를 제한 도메인에 추가했다.

## 열린 범위

실제 DB insert가 가능한 도메인은 아래 세 개뿐이다.

- `characters`
- `enhancementGroups`
- `fieldZones`

세 도메인은 relation 의존도가 비교적 낮아서 신규 row 생성의 제한 적용 범위로 선택했다.

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
- `dropTables`
- `dropTableItems`
- `enhancementLevels`
- `characterSkills`

## Change log

생성이 성공하면 `admin_change_logs`에 `action=create`로 기록한다.

v168부터 create rollback/delete 중 **생성 row 삭제 되돌리기**가 제한적으로 열렸다. v175 기준 대상은 `characters`, `enhancementGroups`, `fieldZones`의 `action=create` 이력이며, 현재값/연결 데이터 검사를 통과해야 한다.

## DB reset / seed

필요 없음.

스키마 변경도 없다.
