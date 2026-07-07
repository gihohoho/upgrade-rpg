# Admin Guarded Edit Apply

v122에서는 관리자 페이지의 마스터 데이터 편집 초안에서 일부 안전한 필드를 실제 DB에 적용할 수 있게 했다.

## 추가 API

```txt
POST /api/v1/admin/master-data/edit-apply
GET /api/v1/admin/change-logs
```

## 적용 흐름

1. 관리자 페이지에서 마스터 데이터 상세를 연다.
2. allow-list에 들어간 필드만 편집 초안에 표시된다.
3. `초안 검증`으로 `POST /api/v1/admin/master-data/edit-preview`를 먼저 실행한다.
4. 확인 문구 `APPLY MASTER DATA EDIT`를 정확히 입력한다.
5. `검증 후 실제 적용`을 누르면 FastAPI가 다시 검증한 뒤 DB에 반영한다.
6. 적용 이력은 `admin_change_logs`에 저장된다.
7. 게임 런타임은 바로 바뀌지 않고, 새로고침 후 최신 master-data를 다시 읽는다.

## 실제 적용 가능한 필드

쓰기 범위는 의도적으로 좁다.

- itemTemplates: `name`, `description`, `grade`, `stackable`, `admin_note`
- skills: `name`, `description`, `proc_rate`, `cooldown_seconds`
- skillLevels: `damage_multiplier`, `proc_rate_bonus`
- bosses: `name`, `tier`, `boss_type`, `hp`, `description`, `cooldown_seconds`, `is_enabled`
- fieldZones: `name`, `sort_order`, `enemy_hp`, `gold_reward`, `description`, `is_enabled`
- characters: `name`, `description`, `is_enabled`
- dropTables: `description`, `is_enabled`
- dropTableItems: `rate`, `min_quantity`, `max_quantity`
- enhancementGroups: `name`, `description`, `max_level`, `is_enabled`
- enhancementLevels: `to_level`, `success_rate`, `gold_cost`
- characterSkills: `sort_order`, `is_default`

## 계속 잠긴 필드

아래 필드는 연결 깨짐 위험이 있어 아직 실제 적용하지 않는다.

- `id`
- `code`
- `*_id`
- `*_code`
- `*_json`
- 이미지/아이콘/asset 필드
- 관계 구조를 바꾸는 필드

## 안전장치

- 적용 전 백엔드가 dry-run 검증 로직을 다시 실행한다.
- 확인 문구가 틀리면 `confirmation_required`로 차단된다.
- 검증 오류가 있거나 변경된 값이 없으면 DB에 반영하지 않는다.
- 적용 성공 시 `admin_change_logs`에 `before_json`, `after_json`, `rollback_json`을 저장한다.
- 관리자 변경 이력 목록은 원본 before/after JSON을 통째로 내려주지 않고 변경 필드명만 요약 표시한다.

## DB reset / seed 필요 없음

기존 `admin_change_logs` 테이블을 사용한다. 새 테이블 추가나 seed 변경이 아니므로 DB reset / seed 필요 없음.

## 확인 방법

```bash
# 위치: backend 폴더 + 가상환경 activate 상태
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

브라우저:

```txt
SAVE DATA → admin → 관리자 페이지 열기
마스터 데이터 카탈로그 → 보기
관리자 편집 초안 → 값 수정
초안 검증
확인 문구 APPLY MASTER DATA EDIT 입력
검증 후 실제 적용
```

Console:

```js
// 위치: 브라우저 개발자도구 Console
readAdminEditDraftValues();
readAdminEditApplyControls();
await previewAdminEditDraft();
await applyAdminEditDraft();
await refreshAdminChangeLogs();
```

## live check

기본 live check는 실제 DB 적용을 하지 않는다. 일부러 틀린 확인 문구로 apply가 차단되는지만 확인한다.

```bash
# 위치: backend 폴더 + 가상환경 activate 상태
python scripts/check_admin_readonly_api.py
```
