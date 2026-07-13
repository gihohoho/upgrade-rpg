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

## 현재 결정

당분간 게임 콘텐츠 개발은 하지 않습니다.

보류:

- 장비/스킬/보스/필드/드랍/강화/밸런스 신규 개발

우선:

- Vue + FastAPI + DB + 배포 직전 구조 준비

## 다음 작업

`v268 프로젝트 구조 점검 + Vue/FastAPI/DB 전환 준비`

해야 할 일:

1. 현재 파일/폴더 구조 분석
2. `admin.html`, `index.html`, `src/`, `backend/`, `tools/`, `docs/` 역할 정리
3. Vue 전환 시 이식/보존/폐기 후보 분류
4. 실제 폴더 이동 전 smoke 경로 의존성 확인
5. 구조 변경 계획 문서화
6. 가능한 경우 무해한 문서 정리만 적용
7. 전체 smoke와 compileall 확인 후 ZIP 생성

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
