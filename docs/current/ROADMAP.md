# Roadmap — v269

## 현재 방향

게임 콘텐츠 개발은 잠시 멈추고, Vue + FastAPI + PostgreSQL + 배포 준비 구조로 전환하기 위한 기반을 만듭니다.

## 완료

### v266 이전

- 관리자 마스터 데이터 카탈로그/상세 조회
- 신규 row 생성 Preview
- 기존 row 편집 Preview
- ChangeLog 조회
- Rollback Preview
- 생성 row 삭제 Preview
- 삭제 row 복원 Preview
- 공통 Unified Diff 렌더러
- 공통 Rollback Snapshot 표시
- Snapshot fingerprint/무결성 검사
- Preview 결과 요약 공통 렌더러
- 고정 fixture Preview 점검 패널
- 실제 Preview API 응답 표시 점검 패널
- Admin Workspace / 업무 모드 / 초보자 안내
- 카탈로그 compact UX
- 날짜/JSON 키 축약 표시
- 긴 값 모달 보기
- 상세 화면 바로가기 버튼 보완

### v268

- 프로젝트 구조 점검
- Vue/FastAPI/DB 전환 문서화
- legacy 경로 1차 영향 분석
- 실제 대이동 보류 결정

### v269

- legacy 경로 의존성 자동 목록화 도구 추가
- `docs/current/LEGACY_PATH_DEPENDENCIES.md` 생성
- Vue 앱 위치 `frontend/vue-app/` 결정
- 기존 root `src/`는 legacy JS/CSS로 유지하기로 확정

## 다음 단계

### v270 — Vue 앱 기본 shell 생성

목표:

- `frontend/vue-app/` 생성
- Vite + Vue 기본 구조 준비
- 실제 관리자/게임 로직 연결 없이 shell만 준비
- legacy smoke 유지
- Vue 기본 build 검증 추가

### v271 — Backend 구조 정리 계획

목표:

- route/service/schema/model/repository 역할 정리
- 기존 route path 유지 전략 문서화
- contract 영향 분석

### v272 — PostgreSQL/Alembic 도입 준비

목표:

- migration/seed/운영 데이터 역할 구분
- rollback snapshot 정책 검토
- 실제 DB 변경 전 smoke/contract 계획 수립

### v273 — 인증 설계 준비

목표:

- 사용자/관리자 권한 정의
- 토큰 저장 방식 결정
- FastAPI dependency 설계
- Vue route guard 설계
- Write Guard와의 관계 정리

## 계속 보류

- 장비 추가
- 스킬 추가
- 보스 추가
- 필드 추가
- 드랍률/밸런스 조정
- 강화 수치 조정
- 신규 콘텐츠 기획 반영
