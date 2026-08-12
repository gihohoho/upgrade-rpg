# Vue Admin Read-only Catalog — v276~v281

## 목적

legacy `admin.html`을 바로 Vue로 대체하지 않고, FastAPI의 안전한 관리자 GET API를 Vue shell에 작은 단위로 옮겨 실제 응답을 확인합니다.

진행 단계:

- v276: 마스터 데이터 도메인 목록
- v277: 선택 도메인의 첫 카탈로그 페이지
- v278: 검색·활성 상태·정렬·페이지네이션
- v279: 선택 row의 안전한 상세 조회
- v280: 선택 row의 관계 그룹 조회
- v281: 관계 row의 상세 이동과 이전 상세 돌아가기

실제 관리자 운영 화면은 계속 루트 `admin.html`입니다. Vue `/admin`은 이식 준비와 조회 검증 화면입니다.

## 현재 GET 연결 범위

```txt
GET /api/v1/health
GET /api/v1/admin/requirements
GET /api/v1/admin/master-data/domains
GET /api/v1/admin/master-data/catalog
GET /api/v1/admin/master-data/detail
GET /api/v1/admin/master-data/relations
```

## v278 — 카탈로그 조회 조건

`GET /api/v1/admin/master-data/catalog`에 `domain`, `limit=20`, `page`, `query`, `enabled`, `sort`만 보냅니다.

- 검색어는 화면에서 80자로 제한합니다.
- 활성 필드가 없는 도메인은 `enabled=all`만 사용합니다.
- 도메인을 바꾸면 검색어, 활성 상태, 정렬, page를 초기화합니다.
- 새 요청 전에 기존 요청을 `AbortController`로 취소합니다.
- 목록을 다시 조회하면 이전 상세 선택과 관계 선택 기록을 해제합니다.

## v279 — 조회 전용 상세

```txt
GET /api/v1/admin/master-data/detail?domain=<domain>&id=<row id>
```

표시 범위:

- scalar 필드
- 관계 개수/코드 힌트
- 축약·마스킹된 JSON 미리보기
- asset 원본 숨김 상태
- warnings

Vue wrapper는 화면의 `rowId`를 backend query 이름 `id`로 변환합니다.

## v280 — 조회 전용 관계 그룹

추가 파일:

- `frontend/vue-app/src/components/AdminMasterRelationsPanel.vue`

호출 API:

```txt
GET /api/v1/admin/master-data/relations?domain=<domain>&id=<row id>&limit=20
```

실제 응답 사용 위치:

```txt
response.payload.groups[]
group.columns[]
group.rows[]
group.count
group.shown
group.limited
```

표시 범위:

- 관계 그룹 이름과 대상 domain
- 전체 관련 row 수와 현재 표시 수
- backend가 제공하는 축약 columns/cells
- 그룹당 20개를 넘을 때 `일부만 표시`
- loading/error/empty/success 상태

원본 JSON과 asset은 요청하거나 표시하지 않습니다. 관계 편집도 제공하지 않습니다.

## v281 — 연관 row 상세 이동

관계 표의 `이 row 상세` 버튼을 누르면 해당 row의 기존 GET detail과 GET relations를 다시 조회합니다.

- 이동 전 선택은 `selectionHistory`에 저장합니다.
- 상세 패널의 `이전 상세로` 버튼으로 직전 row로 돌아갑니다.
- `선택 해제`, 카탈로그 재조회, 도메인 변경 시 선택 기록을 초기화합니다.
- 관계 row 이동은 route/body/write 계약을 바꾸지 않습니다.

## `/requirements` 상태 표시

`response.data.readOnlyOverviewReady`를 사용합니다.

- `true` → `준비 완료`
- `false` 또는 없음 → `확인 필요`

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
- Preview/Apply/write UI 연결
- 기존 smoke/contract 의미
- 게임 콘텐츠

## 설치해야 할 것

v280~v281에서 새 라이브러리나 프레임워크는 추가하지 않았습니다.

이미 `frontend/vue-app/node_modules`가 있다면 다시 설치할 것은 없습니다. 없다면 한 번만 실행합니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

## 실행 방법

FastAPI 가상환경 활성화:

실행 위치: 프로젝트 루트  
`.venv` 상태: 꺼져 있다면 켜야 함

```bash
.venv\Scripts\activate
```

FastAPI 서버:

실행 위치: `backend` 폴더  
`.venv` 상태: 켜진 상태

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Vue 서버:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 필요 없음 / 꺼져 있어도 됨

```bash
npm run dev
```

확인 주소:

```txt
http://127.0.0.1:5173/admin
```

## 사용자가 확인할 사항

1. 카탈로그 `상세 보기`를 누르면 상세와 관계 패널이 함께 표시되는지 확인합니다.
2. 관계가 있는 row에서 그룹별 관련 row 표가 나오는지 확인합니다.
3. 관계가 없는 row는 오류가 아니라 빈 상태 안내가 나오는지 확인합니다.
4. `이 row 상세`를 누르면 연관 row의 상세와 관계로 바뀌는지 확인합니다.
5. `이전 상세로`를 누르면 직전 상세로 돌아오는지 확인합니다.
6. `선택 해제` 후 상세와 관계 패널이 idle 상태가 되는지 확인합니다.
7. 브라우저 콘솔에 CORS 또는 JavaScript 오류가 없는지 확인합니다.

## 다음 안전 단계

다음은 PostgreSQL/Alembic 도입 준비 문서를 현재 backend 모델과 실행 환경 기준으로 구체화합니다. 실제 DB 구조와 `.env`는 사용자 승인 전 변경하지 않습니다.
