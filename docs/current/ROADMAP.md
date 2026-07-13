# Roadmap — v270

## 큰 방향

게임 콘텐츠 추가보다 구조 전환을 먼저 끝냅니다.

목표 구조:

```txt
frontend/vue-app/  -> Vue 화면
backend/           -> FastAPI API
PostgreSQL         -> 운영 DB
admin              -> 안전한 관리자 도구
legacy             -> 전환 완료 전까지 보존
```

## 완료

- v266 관리자 UX 안정화
- v268 프로젝트 구조 점검
- v269 legacy 경로 의존성 자동 목록화
- v270 Vue 기본 shell 생성

## 다음 단계

### v271 — Vue API client 읽기 전용 설계

목표:

- Vue에서 사용할 API client 기본 구조 준비
- 기존 FastAPI route path 목록과 연결 방식 정리
- 읽기 전용 GET 계열부터 시작
- 인증/interceptor/write는 아직 보류

### v272 — Backend 구조 정리 계획

목표:

- FastAPI route/service/schema/model/repository 역할 정리
- 기존 route path 유지 방식 문서화
- backend 구조 이동 전 smoke 영향 분석

### v273 — PostgreSQL/Alembic 준비

목표:

- 실제 DB 구조 변경 전 계획 수립
- migration/seed/운영 데이터 분리
- rollback snapshot/transaction 정책 검토

### v274 — 인증 설계 준비

목표:

- 사용자/관리자 권한 정의
- 토큰 저장 방식 검토
- FastAPI dependency와 Vue route guard 설계
- 기존 Write Guard와 충돌하지 않는 구조 검토

### v275 이후 — Vue 관리자 이식

목표:

- 읽기 전용 카탈로그부터 Vue로 이식
- Preview/Apply/write는 가장 마지막에 이식

## 계속 보류

- 장비 추가
- 스킬 추가
- 보스 추가
- 필드 추가
- 드랍률/밸런스 조정
- 강화 수치 조정
- 신규 콘텐츠 기획 반영
