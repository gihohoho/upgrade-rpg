# Upgrade RPG 다음 채팅 시작 안내

프로젝트 루트에서 다음 문서를 순서대로 읽고 이어서 작업해주세요.

1. [AGENTS.md](AGENTS.md) — 계속 지켜야 할 규칙
2. [NEXT_CHAT_HANDOFF.md](NEXT_CHAT_HANDOFF.md) — 현재 체크포인트와 바로 다음 단계
3. [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md) — 상세 상태와 승인 경계

과거 문서를 처음부터 전부 읽지 말고, 작업에 직접 필요한 경우에만 [Docs Hub](docs/README.md)를 통해 reference, contracts, guides, archive history를 찾아보세요. 현재 다음 단계와 승인 경계는 `NEXT_CHAT_HANDOFF.md`만 기준으로 판단합니다.

문서를 읽은 뒤 완료된 v377 source·private environment·local/Neon migration·Brevo E2E·GitHub/GHCR·Render backend 배포, v378 static 배포, v379 Vue 기반, v380 인증·8칸 캐릭터 gate, v381 관리자 인증·route guard와 v382 관리자 Preview 작업대를 다시 전면 감사하거나 재실행하지 말고 `prepare-vue-admin-apply-confirmation-gates`를 이어서 진행해주세요. 먼저 별도 exact 승인을 받아 Docker Desktop과 기존 프로젝트 PostgreSQL을 시작한 뒤 남은 로컬 로그인 E2E를 확인하세요. Apply 확인 UI는 최신 Preview 재검증·게임식 확인 modal·exact 문구·dev key를 함께 설계하되 실제 Apply endpoint·DB write와 production 관리자 복구는 각각 별도 승인을 받기 전에는 실행하지 마세요. 기존 marker/evidence 삭제·덮어쓰기, 자동 retry, DB reset·seed·restore·stamp·actual downgrade와 남은 공개 gate 우회는 하지 마세요.
