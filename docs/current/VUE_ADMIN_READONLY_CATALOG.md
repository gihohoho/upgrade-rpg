# Vue Admin Read-only Catalog — v276~v279

## 목적

legacy `admin.html`을 바로 Vue로 대체하지 않고, FastAPI의 안전한 관리자 GET API를 Vue shell에 작은 단위로 옮겨 실제 응답을 확인합니다.

진행 단계:

- v276: 마스터 데이터 도메인 목록
- v277: 선택 도메인의 첫 카탈로그 페이지
- v278: 검색·활성 상태·정렬·페이지네이션
- v279: 선택 row의 안전한 상세 조회

실제 관리자 운영 화면은 계속 루트 `admin.html`입니다. Vue `/admin`은 이식 준비와 조회 검증 화면입니다.

## v278 — 카탈로그 조회 조건

호출 API:

```txt
GET /api/v1/admin/master-data/catalog
```

사용 query:

```txt
domain=<선택 도메인>
limit=20
page=<현재 페이지>
query=<검색어>
enabled=all|enabled|disabled
sort=id_asc|code_asc|name_asc|sort_asc|updated_desc
```

안전 경계:

- 검색어는 화면에서 80자로 제한합니다.
- 활성 필드를 지원하지 않는 도메인은 `enabled=all`만 보냅니다.
- 도메인을 바꾸면 검색어, 활성 상태, 정렬, page를 초기화합니다.
- 이전/다음 이동은 backend의 `hasPrevPage`, `hasNextPage`를 사용합니다.
- 새 요청 전에 기존 요청을 `AbortController`로 취소합니다.
- 목록을 다시 조회하면 이전 상세 선택을 해제해 서로 다른 row가 섞이지 않게 합니다.

## v279 — 조회 전용 상세

추가 파일:

- `frontend/vue-app/src/components/AdminMasterDetailPanel.vue`

호출 API:

```txt
GET /api/v1/admin/master-data/detail?domain=<domain>&id=<row id>
```

Vue API wrapper는 화면에서 받은 `rowId`를 backend query 이름 `id`로 변환합니다.

응답 사용 위치:

```txt
response.payload.fields
response.payload.jsonFields
response.payload.assetFields
response.payload.relationHints
```

표시 범위:

- 기본 scalar 필드
- 관계 개수/코드 힌트
- 안전하게 축약·마스킹된 JSON 미리보기
- asset 필드가 숨겨졌는지 여부
- `sanitizedJsonReturned`, `assetsReturned`, warnings

연결하지 않은 것:

- `GET /admin/master-data/relations`
- `relationEditOptions`를 이용한 편집 UI
- 신규 row 생성
- 편집
- Preview/Apply/write
- 인증/token/interceptor

상세 화면은 GET 응답을 표시할 뿐이며 DB를 수정하지 않습니다.

## `/requirements` 상태 표시 개선

`GET /admin/requirements` 응답에는 일반 `status` 문자열이 없어서 이전 화면에서는 성공해도 상세 상태가 `-`로 표시됐습니다.

v279부터는 응답의 아래 값을 사용해 표시합니다.

```txt
response.data.readOnlyOverviewReady
```

- `true` → `준비 완료`
- `false` 또는 없음 → `확인 필요`

요청 성공/실패 판정 방식은 변경하지 않았습니다.

## 변경하지 않은 것

- DB 구조
- `.env`
- seed
- 인증
- 기존 route path
- 기존 API 응답 body
- Write Guard
- 실제 write 로직
- 관리자 Preview/Apply 요청 body
- 기존 smoke/contract 의미
- 게임 콘텐츠

## 설치해야 할 것

v278~v279에서 새 라이브러리나 프레임워크는 추가하지 않았습니다.

이미 `frontend/vue-app/node_modules`가 있다면 다시 설치할 것은 없습니다.
Vue 앱 의존성을 아직 설치하지 않았다면 아래 명령을 한 번만 실행합니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

## 실행 방법

### FastAPI

실행 위치: 프로젝트 루트  
`.venv` 상태: 꺼져 있다면 켜야 함

```bash
.venv\Scripts\activate
```

실행 위치: `backend` 폴더  
`.venv` 상태: 켜진 상태

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Vue

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run dev
```

확인 주소:

```txt
http://127.0.0.1:5173/admin
```

## 사용자가 확인할 사항

1. `/health`는 `ok`, `/admin/requirements`는 `준비 완료`로 보이는지 확인합니다.
2. 검색어를 넣고 `검색`을 누르면 결과와 전체 개수가 바뀌는지 확인합니다.
3. 활성 필드를 지원하는 도메인에서 활성만/비활성만 필터가 동작하는지 확인합니다.
4. 활성 필드를 지원하지 않는 도메인에서는 활성 상태 select가 비활성화되는지 확인합니다.
5. 이전/다음 페이지 버튼과 페이지 숫자가 맞게 바뀌는지 확인합니다.
6. `상세 보기`를 누르면 기본 필드와 JSON 안전 미리보기가 표시되는지 확인합니다.
7. 다른 도메인 또는 다른 조회 조건으로 바꾸면 이전 상세 선택이 해제되는지 확인합니다.
8. 브라우저 콘솔에 CORS 또는 JavaScript 오류가 없는지 확인합니다.

## 다음 안전 단계

다음은 `v280 Vue admin read-only relations panel` 후보입니다.

진행 전 실제 `GET /admin/master-data/relations` 응답 구조를 다시 확인하고, 관계 목록 조회만 연결합니다. Preview/Apply/write는 계속 제외합니다.
