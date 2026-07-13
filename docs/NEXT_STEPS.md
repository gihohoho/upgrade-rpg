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
- legacy 경로 의존성 1차 분석

## 현재 결정

당분간 게임 콘텐츠 개발은 하지 않습니다.

보류:

- 장비/스킬/보스/필드/드랍/강화/밸런스 신규 개발

우선:

- Vue + FastAPI + DB + 배포 직전 구조 준비

## v268 결론

현재 구조는 smoke/contract가 legacy 경로를 직접 많이 참조합니다.

특히 다음 경로는 바로 이동하면 위험합니다.

- `admin.html`
- `index.html`
- `src/api`
- `src/api/admin`
- `backend/app/api/routes`
- `backend/app/services`
- `tools/run_smoke_core.sh`

따라서 지금은 실제 대이동보다, 새 Vue 앱을 기존 구조 옆에 별도로 만드는 방식이 안전합니다.

## 다음 작업

`v269 legacy 경로 의존성 자동 목록화 + Vue 앱 생성 위치 결정`

해야 할 일:

1. smoke가 직접 읽는 파일 경로를 자동으로 목록화합니다.
2. 이동 금지/이식 후보/나중 대체 후보를 더 정확히 나눕니다.
3. `frontend/vue-app/` 생성 여부와 생성 시점을 확정합니다.
4. Vue 앱을 만들더라도 기존 `admin.html`, `index.html`, `src/`는 그대로 둡니다.
5. Vue 기본 검증 명령과 기존 core smoke 검증을 분리합니다.
6. 문서 archive 이동은 아직 하지 말고, 먼저 smoke 영향 분석을 끝냅니다.

## 그다음 작업 후보

### v270 Backend 구조 정리 계획

- FastAPI route/service/schema/model/repository 역할 재정의
- 기존 route path 유지 방식 정리
- contract/readiness 영향 분석

### v271 DB/PostgreSQL/Alembic 준비

- migration/seed/운영 데이터 역할 분리
- DB transaction/rollback snapshot 정책 검토
- 실제 DB 구조 변경은 사용자 승인 후 진행

### v272 인증 설계 준비

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
