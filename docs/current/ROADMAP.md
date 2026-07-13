# 로드맵 — Vue/FastAPI/DB 전환 우선

## 확정된 방향

관리자 HTML 페이지는 v266 수준에서 잠시 고정합니다.
게임 콘텐츠 개발은 Vue + FastAPI + DB + 배포 직전 구조가 갖춰진 뒤에 재개합니다.

## 다음 순서

### v268 — 프로젝트 구조 점검 + 전환 준비

- 현재 파일/폴더 역할 분석
- legacy HTML/JS 유지 범위 정리
- Vue 이식 대상 분류
- FastAPI 구조 정리 영향 범위 조사
- 문서/스모크 경로 영향 분석

### v269 — legacy 분리 계획 또는 1차 무해 정리

- 실제 이동 전 경로 의존성 확인
- 깨질 수 있는 script 경로 목록화
- 필요 시 `legacy/` 이동 계획 문서 작성

### v270 — Backend 구조 정리 계획

- `app/api`, `services`, `schemas`, `models`, `repositories` 역할 재정의
- 현재 route 호환성 유지 방안 정리
- Contract/Smoke 영향 분석

### v271 — DB/PostgreSQL/Alembic 도입 준비

- 현재 DB 관련 파일 확인
- migration과 seed 역할 분리 계획
- 운영 DB 변경 전 로컬/테스트 DB 기준선 정리

### v272 — Vue 앱 초기 세팅 준비

- Vue 프로젝트 위치 결정
- 기존 `admin.html` 이식 우선순위 정리
- API client/interceptor/store/router 구조 계획

### 이후

- Vue 관리자 1차 이식
- Vue 게임 화면 1차 이식
- 인증/배포 설정
- 배포 직전 안정화
- 그다음 게임 콘텐츠 개발 재개
