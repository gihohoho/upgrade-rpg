# 현재 상태 — v267 handoff ready

## 안정 기준

- 최신 인계 ZIP: `rpg_v267_next_chat_handoff_ready.zip`
- 직전 기능 기준: `v266.admin-practical-ux-polish`
- 관리자 readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## 관리자 페이지 상태

현재 `admin.html` 기반 관리자 페이지는 임시 운영/검증 도구로 충분히 안정화했습니다.

가능한 작업:

- 마스터 데이터 카탈로그 조회
- 상세 확인
- 신규 row 생성 Preview
- 편집 Preview
- ChangeLog 조회
- Rollback Preview
- 생성 row 삭제 Preview
- 삭제 row 복원 Preview
- Preview fixture 점검
- Live Preview API 응답 표시 점검
- 공통 Diff/Snapshot/Preview Summary 표시

## v266 UX 상태

- Admin Workspace와 초보자 안내 유지
- 카탈로그 보기 방식 3분할 제거
- 긴 값은 짧은 미리보기 + 모달 전체 보기
- 버튼 위험도는 텍스트 chip 없이 색상/tooltip 중심
- 상세 화면 바로가기 버튼은 실제 섹션 펼침/스크롤 이동

## 현재 방향

당분간 게임 콘텐츠 개발은 하지 않습니다.

다음 우선순위는 Vue/FastAPI/DB/배포 직전 구조를 준비하는 것입니다.

## 안전 원칙

다음은 사용자 승인 없이 변경하지 않습니다.

- DB
- env
- seed
- 인증
- 기존 route path
- API 응답 body
- Write Guard
- 실제 write 로직
