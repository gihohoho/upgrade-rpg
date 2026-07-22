# Next Steps — v336

현재 production image와 isolated runtime 검증은 완료됐고 운영 배포 계획도 검토했습니다. 비용 최소 공급자는 Render Free Web Service Singapore + Neon Free PostgreSQL 16 Singapore로 선택했습니다.

Neon Free PostgreSQL 16 AWS Singapore 프로젝트 생성과 Direct/Pooler read-only TLS 검증은 완료했습니다. 다음에는 기호가 Render Hobby에 로그인합니다. Render에는 처음에 결제수단을 추가하지 않습니다. 로그인 뒤 Codex가 exact GHCR digest, Singapore region, managed HTTPS, secret 이름과 health path를 설정할 준비를 합니다.

모든 입력이 준비되기 전에는 deploy 승인을 열지 않습니다. 입력을 반영한 실행 준비 commit을 만든 뒤 기호가 정확한 40자리 SHA를 별도 승인하면, 그 문서에 적힌 범위에서만 실제 deploy합니다.

Neon의 현재 DB는 기본 `neondb`이고 계획상 운영 DB는 `rpg_game`입니다. DB 생성과 schema/data 초기화·이식은 backend 공개 deploy와 분리해 별도 실행 계획과 승인으로 진행합니다. 세부 목록은 `PRODUCTION_PROVIDER_SELECTION.md`, `PRODUCTION_DEPLOYMENT_PLAN.md`, 전체 순서는 `ROADMAP.md`를 봅니다.
