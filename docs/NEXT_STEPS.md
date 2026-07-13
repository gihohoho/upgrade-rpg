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

## 현재 결정

당분간 게임 콘텐츠 개발은 하지 않습니다.

보류:

- 장비/스킬/보스/필드/드랍/강화/밸런스 신규 개발

우선:

- Vue + FastAPI + DB + 배포 직전 구조 준비

## v270 결론

새 Vue 앱은 다음 위치에 생성했습니다.

```txt
frontend/vue-app/
```

기존 legacy 경로는 그대로 유지합니다.

- `admin.html`
- `index.html`
- 루트 `src/`
- `backend/`
- `tools/`

Vue shell은 실제 게임/관리자 기능을 아직 대체하지 않습니다.

## 사용자가 설치/확인해야 할 것

처음 Vue 앱 실행 전 설치:

실행 위치: `frontend/vue-app` 폴더

```bash
npm install
```

Vue 개발 서버 실행:

실행 위치: `frontend/vue-app` 폴더

```bash
npm run dev
```

브라우저 확인:

```txt
http://127.0.0.1:5173
```

확인할 화면:

- `/game`
- `/admin`

## 다음 작업

`v271 Vue API client 읽기 전용 설계 + backend route map 연결 준비`

해야 할 일:

1. 기존 FastAPI route path 목록을 Vue 쪽 문서와 연결합니다.
2. Vue용 API client 파일 구조를 만듭니다.
3. 처음에는 GET/읽기 전용 API만 대상으로 합니다.
4. 인증/interceptor는 아직 실제 구현하지 않습니다.
5. Preview/Apply/write 요청 body는 건드리지 않습니다.
6. 기존 `admin.html`/`index.html`은 계속 유지합니다.
7. Vue shell smoke와 legacy core smoke를 모두 확인합니다.

## 그다음 작업 후보

### v272 Backend 구조 정리 계획

- FastAPI route/service/schema/model/repository 역할 재정의
- 기존 route path 유지 방식 정리
- contract/readiness 영향 분석

### v273 DB/PostgreSQL/Alembic 준비

- migration/seed/운영 데이터 역할 분리
- DB transaction/rollback snapshot 정책 검토
- 실제 DB 구조 변경은 사용자 승인 후 진행

### v274 인증 설계 준비

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
