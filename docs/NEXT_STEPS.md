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
- 관리자 HTML 페이지는 임시 운영/검증 도구로 충분한 수준까지 안정화
- v268 프로젝트 구조 점검
- Vue/FastAPI/DB 전환 계획 문서 갱신
- v269 legacy 경로 의존성 자동 목록화 도구 추가
- v269 Vue 앱 생성 위치 `frontend/vue-app/` 결정

## 현재 결정

당분간 게임 콘텐츠 개발은 하지 않습니다.

보류:

- 장비/스킬/보스/필드/드랍/강화/밸런스 신규 개발

우선:

- Vue + FastAPI + DB + 배포 직전 구조 준비

## v269 결론

현재 구조는 smoke/contract가 legacy 경로를 직접 많이 참조합니다.

특히 다음 경로는 바로 이동하면 위험합니다.

- `admin.html`
- `index.html`
- `src/`
- `src/api/`
- `src/api/admin/`
- `backend/app/api/routes/`
- `backend/app/services/`
- `backend/seeds/`
- `tools/run_smoke_core.sh`
- `tools/smoke/`

따라서 지금은 `legacy/` 폴더로 대이동하지 않습니다.

새 Vue 앱은 기존 구조 옆의 다음 경로에 만드는 것이 안전합니다.

```txt
frontend/vue-app/
```

## 다음 작업

`v270 Vue 앱 기본 shell 생성`

해야 할 일:

1. 사용자 승인 후 `frontend/vue-app/`에 Vite + Vue 기본 프로젝트를 생성합니다.
2. 기존 `admin.html`, `index.html`, `src/`는 그대로 둡니다.
3. Vue shell에는 처음부터 실제 관리자/게임 로직을 붙이지 않습니다.
4. `AdminShell`, `GameShell` 같은 빈 화면/라우팅 구조만 만듭니다.
5. 기존 legacy smoke와 Vue 기본 검증을 분리합니다.
6. Vue 앱 생성으로 root smoke가 깨지지 않는지 확인합니다.
7. package manager와 실행 명령을 문서화합니다.

## 그다음 작업 후보

### v271 Backend 구조 정리 계획

- FastAPI route/service/schema/model/repository 역할 재정의
- 기존 route path 유지 방식 정리
- contract/readiness 영향 분석

### v272 DB/PostgreSQL/Alembic 준비

- migration/seed/운영 데이터 역할 분리
- DB transaction/rollback snapshot 정책 검토
- 실제 DB 구조 변경은 사용자 승인 후 진행

### v273 인증 설계 준비

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
