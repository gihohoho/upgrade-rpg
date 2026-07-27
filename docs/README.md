# Docs Index — v356

문서는 역할별로 한 곳에만 둡니다. 현재 판단과 과거 기록이 충돌하면 `current/`를 우선합니다.

## 현재 판단

- `current/CURRENT_STATUS.md`: 지금 완료된 상태와 안전 경계
- `current/EQUIPMENT_PROGRESSION_FORMULA_AUDIT.md`: 1~12단계 장비 공식 감사와 12단계 이후 스킬 피해 성장 기준
- `current/PRODUCTION_DEPLOYMENT_PLAN.md`: 검토된 운영 배포 순서·승인·복구 계약
- `current/FRONTEND_STATIC_DEPLOYMENT_PLAN.md`: legacy 게임·관리자 Render Static Site 배포와 exact CORS 승인 계획
- `current/ROADMAP.md`: 다음 진행 순서
- `current/PROJECT_STRUCTURE.md`: 저장소 구조
- `current/SECURITY_ROTATION_AND_GITHUB_GATES.md`: 보안 권한과 나중에 회전할 항목
- `current/BACKEND_IMAGE_GHCR_POLICY.md`: verified GHCR image와 lifecycle 정책
- `current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md`: 공급망 workflow 계약

## 실행 가이드

- `guides/`: 로컬 개발, Git, PostgreSQL, 브라우저 확인, 다음 채팅 시작 가이드
- `contracts/`: API response와 관리자/backend 계약
- `handoff/`: 루트 `NEXT_CHAT_*`의 자동 검사용 mirror

## 과거 기록

- `archive/stage-notes/`: legacy·관리자·backend 단계별 구현 기록
- `archive/postgres-baseline/`: 현재 문서와 중복되지 않는 PostgreSQL/Alembic baseline 기록
- `archive/runtime-hardening/`: runtime hardening 기록
- `archive/production-deployment/`: 완료된 배포 준비 단계와 과거 readiness

완전 동일한 사본은 제거했습니다. Git 이력이 있으므로 삭제된 중복 사본도 과거 commit에서 확인할 수 있습니다. 현재 변경 이력은 `CHANGELOG.md` 하나만 사용합니다.
