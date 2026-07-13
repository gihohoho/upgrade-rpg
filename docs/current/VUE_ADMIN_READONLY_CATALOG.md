# Vue Admin Read-only Catalog — v276~v277

## 목적

legacy `admin.html`을 바로 Vue로 대체하지 않고, FastAPI의 안전한 관리자 GET API를 Vue shell에 작은 단위로 옮겨 실제 응답을 확인합니다.

이번 작업은 두 단계로 진행했습니다.

- v276: 마스터 데이터 도메인 목록 표시
- v277: 선택 도메인의 첫 카탈로그 페이지 표시

실제 관리자 운영 화면은 계속 루트 `admin.html`입니다. Vue `/admin`은 이식 준비와 조회 검증 화면입니다.

## v276 — 도메인 목록 패널

추가 파일:

- `frontend/vue-app/src/components/AdminMasterDomainPanel.vue`

호출 API:

```txt
GET /api/v1/admin/master-data/domains
```

실제 응답에서 도메인 배열은 `data`가 아니라 아래 위치를 사용합니다.

```txt
response.payload.domains
```

기본 도메인은 다음 위치를 사용합니다.

```txt
response.payload.defaultDomain
```

표시하는 정보:

- 도메인 key
- 도메인 한글 label
- 설명
- 전체 row 수
- 활성/비활성 row 수
- 기본 도메인

지원 상태:

- loading
- success
- empty
- error
- 다시 불러오기
- 도메인 선택

도메인 선택은 아래 카탈로그의 조회 대상만 바꾸며 DB를 수정하지 않습니다.

## v277 — 첫 카탈로그 미니 패널

추가 파일:

- `frontend/vue-app/src/components/AdminMasterCatalogMiniPanel.vue`

호출 API:

```txt
GET /api/v1/admin/master-data/catalog
```

고정 조회 범위:

```txt
domain=<선택한 도메인>
limit=20
page=1
sort=id_asc
```

응답 사용 위치:

```txt
response.payload.columns
response.payload.rows
```

표시하는 정보:

- 선택한 도메인 이름
- 현재 row 수
- 전체 row 수
- 현재 페이지/전체 페이지
- backend가 반환한 columns
- 첫 페이지 rows

안전 장치:

- 도메인 변경 시 기존 요청을 `AbortController`로 취소합니다.
- 화면은 backend가 반환한 column/row 구조를 일반 표로만 렌더링합니다.
- 원본 JSON이나 이미지 data URL을 별도로 요청하지 않습니다.
- GET 이외의 요청 method를 사용하지 않습니다.

## 이번 단계에서 연결하지 않은 것

- 검색
- 활성/비활성 필터
- 정렬 변경
- 페이지네이션
- 상세 조회
- 관계 조회
- 신규 row 생성
- 편집
- Preview/Apply/write
- 인증/token/interceptor

Preview/Apply/write route와 요청 body는 기존 contract를 그대로 유지하며 Vue에서 호출하지 않습니다.

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

v276~v277에서 새 라이브러리나 프레임워크는 추가하지 않았습니다.

이미 `frontend/vue-app/node_modules`가 있다면 새로 설치할 것은 없습니다.
Vue 앱 의존성을 아직 한 번도 설치하지 않았다면 아래 명령을 한 번만 실행합니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

## 실행 방법

### FastAPI

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜야 함

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

확인할 사항:

1. `/health`, `/admin/requirements`가 성공으로 표시되는지 확인합니다.
2. 마스터 데이터 도메인 카드가 표시되는지 확인합니다.
3. 기본 도메인 `itemTemplates`가 선택되는지 확인합니다.
4. 선택한 도메인의 첫 20개 카탈로그가 표로 표시되는지 확인합니다.
5. 다른 도메인 카드를 누르면 아래 표가 해당 도메인으로 바뀌는지 확인합니다.
6. 브라우저 콘솔에 CORS 또는 JavaScript 오류가 없는지 확인합니다.

## 다음 안전 단계

다음 단계에서는 현재 미니 카탈로그의 범위를 유지하면서 아래 중 하나만 선택합니다.

1. 검색/활성 필터/페이지네이션을 GET query로 추가
2. 선택 row의 read-only detail을 별도 패널로 추가

둘을 동시에 크게 확장하지 않고 전용 smoke와 실제 응답을 먼저 확인합니다.
