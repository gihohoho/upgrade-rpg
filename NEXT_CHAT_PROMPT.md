# Upgrade RPG 다음 채팅 시작 안내

프로젝트 루트에서 다음 문서를 순서대로 읽고 이어서 작업해주세요.

1. [AGENTS.md](AGENTS.md) — 계속 지켜야 할 규칙
2. [NEXT_CHAT_HANDOFF.md](NEXT_CHAT_HANDOFF.md) — 현재 체크포인트와 바로 다음 단계
3. [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md) — 상세 상태와 승인 경계

과거 문서를 처음부터 전부 읽지 말고, 작업에 직접 필요한 경우에만 [Docs Hub](docs/README.md)를 통해 reference, contracts, guides, archive history를 찾아보세요. 현재 다음 단계와 승인 경계는 `NEXT_CHAT_HANDOFF.md`만 기준으로 판단합니다.

문서를 읽은 뒤 완료된 v377 source·private environment·local/Neon migration·Brevo E2E·GitHub/GHCR·Render backend 배포, v378 static 배포, v379 Vue TypeScript·Pinia 기반과 v380 Vue 인증·8칸 캐릭터 gate를 다시 전면 감사하거나 재실행하지 말고 `migrate-vue-admin-auth-routing`을 이어서 진행해주세요. 기존 관리자 read-only 화면을 typed component/store로 정리하고 account store의 `isAdmin`을 기준으로 route guard와 비관리자 UI 비렌더링을 연결하세요. production 관리자 복구는 이식 작업과 분리하며 exact DB-write 승인을 받기 전에는 실행하지 마세요. 기존 marker/evidence 삭제·덮어쓰기, 자동 retry, DB reset·seed·restore·stamp·actual downgrade와 남은 공개 gate 우회는 하지 마세요.
