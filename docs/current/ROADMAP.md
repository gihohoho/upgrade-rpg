# 로드맵 — Vue/FastAPI/DB 전환 우선

## 확정된 방향

관리자 HTML 페이지는 v266 수준에서 잠시 고정합니다.
게임 콘텐츠 개발은 Vue + FastAPI + DB + 배포 직전 구조가 갖춰진 뒤에 재개합니다.

## v268 완료 — 프로젝트 구조 점검 + 전환 준비

완료한 일:

- 현재 파일/폴더 역할 분석
- legacy HTML/JS 유지 범위 정리
- Vue 이식 대상 분류
- FastAPI 구조 정리 전 영향 범위 조사
- smoke 경로 의존성 1차 분석
- 실제 대이동 보류 결정
- 전환 계획 문서 갱신

핵심 결론:

- `admin.html`, `index.html`, `src/api`, `backend/app/api/routes`, `backend/app/services`는 smoke/contract가 많이 참조합니다.
- 따라서 지금 당장 `legacy/`로 이동하면 검증 경로가 깨질 가능성이 큽니다.
- 다음 단계는 새 Vue 앱을 기존 legacy 옆에 만드는 방향으로 검토합니다.

## 다음 순서

### v269 — legacy 경로 의존성 자동 목록화 + Vue 앱 생성 위치 결정

- smoke가 직접 읽는 파일 경로 목록 자동 추출
- `frontend/vue-app/` 생성 여부 결정
- Vue 앱을 만들더라도 기존 `admin.html`/`index.html`은 유지
- 기존 smoke와 Vue 기본 검증을 분리

### v270 — Backend 구조 정리 계획

- `app/api`, `services`, `schemas`, `models`, `repositories` 역할 재정의
- 현재 route 호환성 유지 방안 정리
- Contract/Smoke 영향 분석
- 실제 route path 변경 없이 내부 구조만 정리할 수 있는지 검토

### v271 — DB/PostgreSQL/Alembic 도입 준비

- 현재 DB 관련 파일 확인
- migration과 seed 역할 분리 계획
- 운영 DB 변경 전 로컬/테스트 DB 기준선 정리
- rollback snapshot 정책과 DB transaction 정책 검토

### v272 — 인증 설계 준비

- 사용자/관리자 권한 구분
- FastAPI dependency 설계
- Vue route guard 설계
- 기존 Write Guard와 인증의 관계 정리
- 인증 contract/smoke 설계

### v273 — Vue 앱 초기 세팅

- `frontend/vue-app/` 생성
- Vite/Vue 기본 실행 확인
- API client 초안 작성
- 기존 legacy 화면과 충돌하지 않게 분리

### v274 이후 — 관리자 Vue 이식

- 읽기 전용 overview부터 이식
- master catalog/detail 이식
- Preview/Diff/Snapshot 공통 렌더러 이식
- write 계열은 가장 마지막에 이식

### 이후 — 게임 화면 Vue 이식

- 게임 콘텐츠 추가 없이 현재 동작을 Vue로 재현
- state/store 분리
- UI component 분리
- save/load 연동 확인

### 배포 직전 안정화

- env 문서화
- DB migration/seed 절차
- 인증/권한 검증
- CORS/정적 파일/SPA fallback 정책
- 백업/복구 정책
- smoke/contract CI화
