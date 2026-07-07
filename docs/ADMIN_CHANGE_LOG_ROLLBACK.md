# Admin Change Log Rollback

v123에서는 관리자 페이지에서 실제 적용된 마스터 데이터 변경 이력을 상세 확인하고, 안전 검사를 통과한 경우 이전 값으로 되돌릴 수 있습니다.

## 추가 API

- `GET /api/v1/admin/change-logs/{change_log_id}`
- `POST /api/v1/admin/change-logs/{change_log_id}/rollback-preview`
- `POST /api/v1/admin/change-logs/{change_log_id}/rollback-apply`

## 관리자 페이지 흐름

1. 관리자 페이지 열기
2. `관리자 변경 이력`에서 `보기` 클릭
3. 변경된 필드의 이전 값 / 적용 값을 확인
4. `되돌리기 미리보기` 클릭
5. 현재 DB 값이 변경 이력의 `after` 값과 일치하면 rollback 가능
6. 확인 문구 입력 후 `검사 후 되돌리기`

확인 문구:

```txt
ROLLBACK MASTER DATA EDIT
```

## 안전장치

되돌리기는 단순히 예전 값을 덮어쓰지 않습니다.

```txt
현재 DB 값
= 변경 이력에 저장된 after 값
```

이 조건이 맞을 때만 되돌리기가 가능합니다.

즉, A 변경 이후 같은 보스/아이템이 다시 수정됐다면, 예전 변경 이력으로 되돌려서 최신 변경을 덮어쓰는 일을 막습니다.

## stackable 설명 보강

관리자 페이지 필드 도움말에 `stackable` 설명을 추가했습니다.

```txt
true  = 같은 아이템을 한 칸에 수량으로 합칠 수 있음
false = 같은 이름이어도 각각 별도 칸을 사용함
```

예시:

```txt
재료 / 강화권: 보통 true
무기 / 방어구 / 탈리스만 / 개별 강화 장비: 보통 false
```

## DB reset / seed 필요 여부

필요 없음.

기존 `admin_change_logs` 테이블의 `before_json`, `after_json`, `rollback_json`을 사용합니다.
새 테이블이나 seed 변경은 없습니다.
