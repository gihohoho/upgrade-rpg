# Admin Read-only Page

Version: `v113: admin page URL helper`

## 목적

`SAVE DATA` 배지 안의 관리자 overview 모달 다음 단계로, 게임 화면과 분리된 정적 관리자 페이지 뼈대를 추가한다.

현재 단계는 **읽기 전용**이다.

- DB 수정 없음
- localStorage 수정 없음
- 게임 런타임 수정 없음
- 원본 `snapshot_json` 표시 없음
- 관리자 지급/수정/삭제 버튼 없음

## 추가 파일

- `admin.html`
- `src/api/admin-page-readonly.js`
- `tools/smoke_admin_readonly_page.js`

## 확인 방법

백엔드 실행:

```bash
# 위치: backend 폴더 + 가상환경 activate 상태
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

게임 화면에서:

```txt
SAVE DATA → admin → 관리자 페이지 열기
```

직접 주소창에 입력할 때는 고정된 `5500` 포트를 쓰지 말고, **현재 게임이 열린 주소와 같은 host/port 기준**으로 `admin.html`을 연다.

예시:

```txt
게임: http://127.0.0.1:5501/index.html
관리자: http://127.0.0.1:5501/admin.html
```

관리자 페이지 상단의 `현재 관리자 페이지 주소` 영역에서 실제 URL을 확인하고 복사할 수 있다.

## 페이지에서 보여주는 것

- read-only 상태
- 마스터 데이터 row count
- 유저 수 요약
- DB 세이브 슬롯 요약
- 최근 세이브 스냅샷 요약
- 관리자 쓰기 UI 차단 상태

## API URL

기본값:

```txt
http://127.0.0.1:8000/api/v1
```

페이지 상단에서 API URL을 바꿔 저장할 수 있다. 저장값은 기존 `upgradeRpgApiBaseUrl` localStorage 키를 재사용한다.

## DB reset / seed

필요 없음.

기존 read-only API만 호출한다.

## v113 추가 사항

- overview 모달의 `관리자 페이지 열기`가 `new URL("admin.html", window.location.href)` 기준으로 실제 관리자 URL을 계산한다.
- overview 모달에 현재 게임 주소 기준 관리자 URL과 `주소 복사` 버튼을 추가했다.
- `admin.html` 상단에 현재 관리자 페이지 주소를 표시하고 복사할 수 있게 했다.
- `게임으로 돌아가기` 링크도 현재 관리자 페이지와 같은 host/port 기준 `index.html`로 보정한다.
- `http://127.0.0.1:5500/admin.html`처럼 특정 포트를 고정 안내하지 않는다.
