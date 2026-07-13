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

## 현재 결정

당분간 게임 콘텐츠 개발은 하지 않습니다.

보류:

- 장비/스킬/보스/필드/드랍/강화/밸런스 신규 개발

우선:

- Vue + FastAPI + DB + 배포 직전 구조 준비

## v273 결론

새 Vue 앱은 다음 위치에 유지합니다.

```txt
frontend/vue-app/
```

v272에서 Vue 화면에 실제 연결한 안전 GET API:

```txt
GET /health
GET /admin/requirements
```

기존 legacy 경로는 그대로 유지합니다.

- `admin.html`
- `index.html`
- 루트 `src/`
- `backend/`
- `tools/`

Preview/Apply/write 요청은 아직 Vue에 연결하지 않았습니다.

v273에서는 Vue 개발 서버 `http://127.0.0.1:5173`에서 FastAPI API 호출이 CORS로 막히지 않도록 local/debug CORS origin을 보강했습니다.

## 사용자가 설치/확인해야 할 것

v273에서 새 라이브러리는 추가하지 않았습니다.

처음 Vue 앱 실행 전 설치:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

FastAPI 서버 실행:

주의: v273 CORS 수정은 FastAPI 서버를 재시작해야 반영됩니다.

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜야 함

```bash
.venv\\Scripts\\activate
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

확인할 것:

- FastAPI 서버가 켜져 있으면 API 상태가 `성공`으로 보입니다.
- FastAPI 서버가 꺼져 있으면 API 상태가 `오류`로 보입니다. 이때도 Vue 화면 전체가 깨지지 않으면 정상입니다.

## 다음 작업

`v274 FastAPI 구조 정리 계획 구체화`

해야 할 일:

1. 현재 `backend/app/api/routes`, `backend/app/services`, `backend/app/schemas`, `backend/app/models` 역할을 실제 파일 기준으로 정리합니다.
2. Vue에서 앞으로 사용할 read-only API와 기존 legacy 유지 API를 구분합니다.
3. route path/API response body는 변경하지 않습니다.
4. DB/Alembic/인증은 실제 변경하지 않고 계획만 문서화합니다.
5. 기존 smoke/contract 의미를 깨지 않는지 영향 범위를 확인합니다.

## 그다음 작업 후보

### v275 DB/PostgreSQL/Alembic 준비

- migration/seed/운영 데이터 역할 분리
- DB transaction/rollback snapshot 정책 검토
- 실제 DB 구조 변경은 사용자 승인 후 진행

### v276 인증 설계 준비

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
