# Admin Safe Apply Review

현재 기준: **v138 admin safe apply review**

관리자 마스터 데이터 편집 초안에서 실제 적용 전에 바뀌는 값만 before/after 형태로 더 크게 확인할 수 있도록 UI를 강화했습니다.

## 변경 내용

- 편집 초안 아래에 `적용 직전 비교` 영역을 추가했습니다.
- 값이 바뀐 필드만 모아서 보여줍니다.
- 변경 필드는 위험도 순서로 정렬합니다.
  - high
  - medium
  - low
- high risk 변경이 있으면 비교 영역 상단에 강한 경고를 표시합니다.
- high risk 변경을 실제 적용하려면 기존 확인 문구 외에 추가 확인 문구도 입력해야 합니다.

## 실제 적용 확인 문구

기존 확인 문구는 그대로 유지합니다.

```txt
APPLY MASTER DATA EDIT
```

high risk 변경이 하나라도 있으면 추가 확인 문구가 필요합니다.

```txt
HIGH RISK EDIT
```

## high risk 예시

- `itemTemplates.stackable`
- `itemTemplates.item_type`
- `itemTemplates.equip_slot`
- `skills.slot_key`
- `skills.proc_rate`
- `skills.cooldown_seconds`
- `bosses.hp`
- `bosses.is_enabled`
- `dropTableItems.rate`
- `dropTableItems.min_quantity`
- `dropTableItems.max_quantity`
- `enhancementLevels.success_rate`
- `enhancementLevels.gold_cost`

## 안전 원칙

- 기존 dev key guard는 유지합니다.
- 기존 stale guard는 유지합니다.
- 기존 백엔드 dry-run 검증은 유지합니다.
- 기존 change log 기록은 유지합니다.
- 기존 post-edit master-data API 자동 확인은 유지합니다.
- 이 단계는 관리자 프론트 UI 안전장치 중심이라 DB reset / seed는 필요 없습니다.
