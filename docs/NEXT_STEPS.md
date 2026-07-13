# 다음 추천 단계

## 현재 완료

- v268~v275 구조/route/read-only client 준비
- v276 Vue 관리자 도메인 목록 패널
- v277 Vue 관리자 첫 카탈로그 미니 패널

현재 Vue `/admin`에서는 GET만 사용합니다.

```txt
GET /api/v1/health
GET /api/v1/admin/requirements
GET /api/v1/admin/master-data/domains
GET /api/v1/admin/master-data/catalog
```

## 현재 보류

- detail/relations
- 모든 Preview/Apply/write
- 인증/token/interceptor
- DB/Alembic 실제 변경
- env/seed 변경
- 게임 콘텐츠

## 다음 작업 — v278

`Vue admin catalog query controls`

추천 범위:

1. 검색어 입력
2. 활성/비활성 필터
3. 이전/다음 페이지
4. backend GET query와 화면 상태 연결
5. 도메인 변경 시 필터/페이지 초기화
6. stale request 취소 유지
7. 전용 smoke 추가

이번 다음 단계에서도 detail/relations와 Preview/Apply/write는 연결하지 않습니다.

## 설치 관련

v277까지 새 라이브러리/프레임워크는 없습니다.

Vue를 처음 실행하는 경우에만:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

Vue 실행:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run dev
```

FastAPI 실행 전 가상환경:

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
