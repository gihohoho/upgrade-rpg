# Upgrade RPG Docs Hub

문서는 **현재 → 참고 → 계약/가이드 → 역사** 순서로 읽습니다. 새 채팅에서 전체 문서를 한꺼번에 읽지 않습니다.

## 1. 지금 상태

- [Current Status](current/CURRENT_STATUS.md): 구현·검증·승인 경계
- [Email Account Lifecycle](current/ACCOUNT_EMAIL_VERIFICATION_RECOVERY_AND_DELETION.md): v371 이메일 인증·복구·삭제
- [Account and Character Slots](current/ACCOUNT_AUTH_AND_CHARACTER_SLOTS.md): 인증과 계정별 8슬롯
- [Security Gates](current/SECURITY_ROTATION_AND_GITHUB_GATES.md): secret·회전·공개 전 보안 gate
- [Production Plan](current/PRODUCTION_DEPLOYMENT_PLAN.md): 운영 배포 승인 단위와 rollback
- [Current Index](current/README.md): 현재 문서 전체 목록

## 2. 계속 쓰는 기술 자료

- `reference/database/`: PostgreSQL, Alembic, Neon, backup/restore runbook
- `reference/backend/`: backend 구조와 blocking-I/O 감사
- `reference/frontend/`: Vue 전환, CORS, read-only API 자료
- `reference/assets/`: 장비 공식과 생성형 이미지 규칙·매핑

## 3. 자동 생성·계약·실행 안내

- `generated/`: route map, backend structure, legacy dependency, Alembic readiness 보고서
- `contracts/`: API response와 관리자 계약
- `guides/`: 로컬 개발, Git, PostgreSQL, 브라우저 확인 절차

## 4. 과거 기록

- `archive/history/`: 완료된 150개 이상의 단계 메모를 주제별로 합친 검색용 역사
- 과거 기록은 현재 규칙이 아닙니다. 현재 문서와 충돌하면 `current/`를 우선합니다.
- 원본 개별 파일은 Git history에서 복원할 수 있습니다.

문서를 새로 만들거나 이동하기 전에는 [Documentation System](DOCUMENTATION_SYSTEM.md)의 위치·중복·크기 규칙을 따릅니다.
