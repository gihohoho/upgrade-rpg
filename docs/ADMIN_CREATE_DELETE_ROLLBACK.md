# Admin Create Delete Rollback

v168에서는 `create-apply`로 새로 만든 제한 도메인 row를 안전하게 삭제 되돌리기할 수 있는 흐름을 추가했다.

## 열린 범위

아직 전체 도메인을 삭제할 수 있게 연 것이 아니다.

대상은 `action=create` 변경 이력 중 아래 도메인만이다.

- `characters`
- `enhancementGroups`

두 도메인은 v165에서 실제 생성이 열린 제한 도메인과 동일하다.

## 안전 검사

삭제 적용 전 preview에서 아래를 모두 검사한다.

- change log가 실제 `action=create`인지 확인
- rollback_json에 `delete: true`가 있는지 확인
- 대상 row가 아직 DB에 존재하는지 확인
- 현재 DB 값이 생성 당시 `after_json` 값과 같은지 확인
- 연결 데이터가 남아 있는지 확인

응답에는 `currentMatchesCreateValues`, `dependencyChecks`, `dependencyBlockerCount`가 포함된다.

## 연결 데이터 차단

`characters` 삭제는 아래 참조가 있으면 차단한다.

- `characterSkills.character_code`
- `userCharacterSkills.character_code`
- `userEquipmentSlots.character_code`
- `userProfiles.current_character_id`

`enhancementGroups` 삭제는 아래 참조가 있으면 차단한다.

- `enhancementLevels.group_code`
- `itemTemplates.enhance_group_code`

## 적용 조건

실제 삭제 적용에는 아래가 모두 필요하다.

- 관리자 쓰기 dev key
- 삭제 preview 통과
- 정확한 확인 문구 `DELETE CREATED MASTER DATA ROW`
- 연결 데이터 blocker 0개
- 현재값이 생성 당시 값과 일치

## Change log

삭제가 성공하면 `admin_change_logs`에 `action=create_delete`로 기록한다.

삭제된 row의 자동 복원은 아직 잠겨 있다. 필요하면 다음 단계에서 restore preview부터 별도로 설계한다.

## DB reset / seed

필요 없음.

스키마 변경도 없다.
