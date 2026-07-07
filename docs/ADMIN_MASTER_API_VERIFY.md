# Admin Master Data API Verify

v127에서 관리자 상세 화면에 **인게임 master-data API 반영 확인** 진단을 추가했습니다.

## 목적

관리자 페이지에서 마스터 데이터를 실제 DB에 적용한 뒤, 게임이 읽는 `/api/v1/game/master-data` 응답에도 같은 값이 내려오는지 바로 확인합니다.

이 기능은 다음 흐름을 확인합니다.

```txt
관리자 DB 값
→ FastAPI /game/master-data 응답
→ 게임 새로고침 후 적용 가능 상태
```

현재 열려 있는 게임 화면의 런타임 객체를 직접 바꾸지는 않습니다. 이미 열려 있던 게임은 새로고침해야 최신 master-data를 다시 읽습니다.

## 사용 방법

1. 관리자 페이지를 엽니다.
2. 마스터 데이터 카탈로그에서 항목 하나의 `보기`를 누릅니다.
3. 상세 화면의 `인게임 master-data API 반영 확인` 영역에서 `선택 항목 API 반영 확인`을 누릅니다.
4. 관리자 상세 값과 `/game/master-data` 응답 값이 같은지 확인합니다.

## 비교 대상

대표적으로 아래 필드를 비교합니다.

- 아이템 템플릿: `name`, `grade`, `description`, `stackable`, `enhance_group_code`, `admin_note`
- 보스: `name`, `tier`, `boss_type`, `hp`, `description`, `cooldown_seconds`, `is_enabled`
- 필드: `name`, `sort_order`, `enemy_hp`, `gold_reward`, `description`, `is_enabled`
- 스킬/드랍/강화 관련 주요 스칼라 필드

## 안전장치

- DB 수정 없음
- localStorage 수정 없음
- 현재 게임 런타임 수정 없음
- `/game/master-data` 조회만 수행
- 차이가 있으면 diff로 표시

## Console helper

```js
// 위치: 브라우저 개발자도구 Console
await verifySelectedMasterDataApi();
```

## DB reset / seed

필요 없습니다.
