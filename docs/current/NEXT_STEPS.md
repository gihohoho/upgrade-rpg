# Next Steps — v338

현재 production image와 isolated runtime 검증은 완료됐고 운영 배포 계획도 검토했습니다. 비용 최소 공급자는 Render Free Web Service Singapore + Neon Free PostgreSQL 16 Singapore로 선택했습니다.

Neon Free PostgreSQL 16 AWS Singapore 프로젝트 생성과 Direct/Pooler read-only TLS 검증은 완료했습니다. Render는 `Hobby (legacy)`이고 결제수단이 없으며, `Existing Image`와 GitHub registry credential 양식까지 읽기 전용으로 확인했습니다.

GitHub `Confirm access`, Render 전용 `read:packages` classic PAT 저장, verified exact digest `Connect`까지 완료했습니다. Render는 서비스 설정 화면에 있으며 Web Service 생성/deploy는 하지 않았습니다.

다음에는 Render Free Singapore 서비스의 이름·리전·instance·health check·환경변수 inventory·auto-deploy 차단값을 정적으로 검토합니다. 동시에 현재 Neon 기본 `neondb`와 계획상 `rpg_game` 차이를 포함한 DB 초기화·이식 계획을 별도 문서로 확정합니다. 이 검토 단계에서는 `Deploy Web Service`, DB write, Alembic mutation을 실행하지 않습니다.

모든 입력이 준비되기 전에는 deploy 승인을 열지 않습니다. 입력을 반영한 실행 준비 commit을 만든 뒤 기호가 정확한 40자리 SHA를 별도 승인하면, 그 문서에 적힌 범위에서만 실제 deploy합니다.

Neon의 현재 DB는 기본 `neondb`이고 계획상 운영 DB는 `rpg_game`입니다. DB 생성과 schema/data 초기화·이식은 backend 공개 deploy와 분리해 별도 실행 계획과 승인으로 진행합니다. 세부 목록은 `PRODUCTION_PROVIDER_SELECTION.md`, `PRODUCTION_DEPLOYMENT_PLAN.md`, 전체 순서는 `ROADMAP.md`를 봅니다.
