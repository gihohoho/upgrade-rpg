# v114 관리자 세이브 스냅샷 필터

## 목적

`admin.html`의 최근 세이브 스냅샷 목록이 많아질 때를 대비해, **읽기 전용 필터**를 추가했다.

이 단계는 여전히 관리자 조회 화면이다.

- DB 수정 없음
- localStorage 수정 없음
- 게임 런타임 수정 없음
- 원본 `snapshot_json` 표시 없음
- 관리자 지급/수정/삭제 버튼 없음

## 추가 API query

기존 API는 그대로 사용한다.

```txt
GET /api/v1/admin/save-snapshots
```

추가 query:

```txt
limit=30
userId=1
slotKey=default
source=localStorage
defaultOnly=true
sort=updated_desc
```

지원 정렬:

```txt
updated_desc  최근 수정순
updated_asc   오래된 수정순
user_asc      유저/슬롯순
slot_asc      슬롯/유저순
```

## 안전장치

- 필터는 조회 조건만 바꾼다.
- `snapshot_json` 원본은 계속 내려주지 않는다.
- `rawSnapshotReturned=false` 유지.
- `slotKey` 필터는 영문/숫자/`.`/`_`/`-`만 허용한다.
- `defaultOnly=true`이면 `slotKey`는 `default`로 고정된다.

## 관리자 페이지 UI

`admin.html`에 아래 필터가 추가됐다.

```txt
표시 개수
유저 ID
슬롯
출처
default만
정렬
```

## 확인 방법

백엔드 실행:

```bash
# 위치: backend 폴더 + 가상환경 activate 상태
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

관리자 페이지:

```txt
SAVE DATA → admin → 관리자 페이지 열기
```

또는 이미 알고 있는 실제 관리자 URL의 `admin.html`을 연다.

API live 체크:

```bash
# 위치: backend 폴더 + 가상환경 activate 상태
python scripts/check_admin_readonly_api.py
```

정적 smoke:

```bash
# 위치: 프로젝트 루트
node tools/smoke_admin_save_snapshot_filters.js
node tools/smoke_admin_readonly_page.js
python tools/smoke_admin_readonly_api_structure.py
```

## DB reset / seed

필요 없음.

기존 `user_save_snapshots` 테이블을 조회만 한다.
