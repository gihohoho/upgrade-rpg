# 다음 추천 단계

## 현재 완료

- 관리자 Preview/Diff/Snapshot/Result Summary 공통화
- Rollback Snapshot 방향/무결성 검사
- Preview fixture 점검 패널
- Live Preview API 응답 표시 점검 패널
- Admin Workspace와 초보자 안내
- 카탈로그 compact UX
- 긴 값 모달
- 상세 화면 바로가기 버튼 보완
- v268 프로젝트 구조 점검
- v269 legacy 경로 의존성 자동 목록화
- v270 Vue 기본 shell 생성
- v271 Vue 읽기 전용 API client 준비
- v272 Vue read-only API smoke 화면 연결
- v273 Vue 개발 서버 local CORS 오류 수정
- v274 FastAPI 구조 정리 계획 구체화
- v275 Backend route map 자동 보고서 + Vue read-only route 후보 확정

## 현재 결정

당분간 게임 콘텐츠 개발은 하지 않습니다.

보류:

- 장비/스킬/보스/필드/드랍/강화/밸런스 신규 개발

우선:

- Vue + FastAPI + DB + 배포 직전 구조 준비

## v275 결론

새 Vue 앱은 계속 아래 위치에 유지합니다.

```txt
frontend/vue-app/
```

기존 legacy 경로는 그대로 유지합니다.

- `admin.html`
- `index.html`
- 루트 `src/`
- `backend/`
- `tools/`

FastAPI route map은 자동 보고서로 관리합니다.

- 보고서: `docs/current/BACKEND_ROUTE_MAP.md`
- 생성/검사 도구: `tools/report_backend_route_map.py`
- smoke: `tools/smoke/backend/smoke_backend_route_map_report.py`

현재 Vue 자동 smoke 화면에 연결된 route:

- `GET /api/v1/health`
- `GET /api/v1/admin/requirements`

다음 연결 후보:

- `GET /api/v1/admin/master-data/domains`

계속 보류:

- 관리자 Preview 계열 POST
- 관리자 Apply/write 계열 POST
- `POST /api/v1/game/save`
- 인증/권한/Write Guard가 필요한 route

## 사용자가 설치/확인해야 할 것

v275에서 새 라이브러리/프레임워크는 추가하지 않았습니다.

처음 Vue 앱 실행 전 설치:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

FastAPI 서버 실행:

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

Vue 개발 서버 실행:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run dev
```

브라우저 확인:

```txt
http://127.0.0.1:5173/game
http://127.0.0.1:5173/admin
```

## 다음 작업

`v276 Vue admin read-only catalog mini panel`

해야 할 일:

1. Vue 관리자 shell에 작은 read-only 카탈로그 점검 패널을 추가합니다.
2. 첫 연결은 `GET /api/v1/admin/master-data/domains`만 사용합니다.
3. 성공/오류/빈 데이터 상태를 표시합니다.
4. catalog row 목록/detail/relations는 아직 자동 호출하지 않습니다.
5. Preview/Apply/write route는 계속 보류합니다.
6. route path/API response body는 변경하지 않습니다.
7. DB/Alembic/인증/env/seed는 실제 변경하지 않습니다.

## 그다음 작업 후보

### v277 DB/PostgreSQL/Alembic 준비

- migration/seed/운영 데이터 역할 분리
- DB transaction/rollback snapshot 정책 검토
- 실제 DB 구조 변경은 사용자 승인 후 진행

### v278 인증 설계 준비

- 사용자/관리자 권한 정의
- token 저장 방식 결정
- FastAPI dependency와 Vue route guard 설계
- 기존 Write Guard와의 관계 정리

## 주의

다음은 사용자 승인 전 변경하지 않습니다.

- DB
- env
- seed
- 인증
- route path
- API 응답 body
- Write Guard
- 실제 write 로직
- 관리자 Preview/Apply 요청 body
- 기존 Smoke/Contract 의미
