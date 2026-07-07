# Admin Edit Stale Guard

v131에서는 관리자 편집 적용 전에 **편집 화면을 열었을 때의 기준값**과 **현재 DB 값**이 같은지 검사하는 stale guard를 추가했습니다.

## 왜 필요한가

관리자 페이지를 열어둔 사이에 같은 데이터를 다른 변경 이력/되돌리기/다른 브라우저에서 먼저 바꿀 수 있습니다.
그 상태에서 오래된 화면의 초안을 그대로 적용하면 최신 DB 값을 덮어쓸 수 있습니다.

예:

1. 관리자가 보스 HP `1000`인 화면을 열어둠
2. 다른 작업으로 같은 보스 HP가 `2000`으로 변경됨
3. 오래된 화면에서 HP `1500`을 적용하려고 함
4. v131부터는 `화면 열 때 값 1000`과 `현재 DB 값 2000`이 다르므로 적용을 차단함

## 적용 방식

프론트는 편집 초안의 현재 값과 함께 `baseValues`를 보냅니다.

```txt
POST /api/v1/admin/master-data/edit-preview
POST /api/v1/admin/master-data/edit-apply
```

백엔드는 각 필드에 대해 다음을 비교합니다.

```txt
baseValues[field] == current DB value
```

다르면 `staleChanges`에 표시하고 `wouldBeValid=false`로 차단합니다.

## 관리자 화면 표시

초안 검증 결과에 다음 항목이 추가됩니다.

```txt
stale guard: on/off
stale count
오래된 초안 검사 표
```

오래된 초안이 감지되면, 해당 상세를 다시 열고 최신 DB 값을 기준으로 다시 수정해야 합니다.

## DB reset / seed 필요 여부

필요 없음.

DB 구조 변경 없이 관리자 편집 API payload와 검증 로직만 강화했습니다.
