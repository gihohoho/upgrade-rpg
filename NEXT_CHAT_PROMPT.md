# Upgrade RPG 다음 채팅 시작 안내

프로젝트 루트에서 다음 문서를 순서대로 읽고 이어서 작업해주세요.

1. [AGENTS.md](AGENTS.md) — 계속 지켜야 할 규칙
2. [NEXT_CHAT_HANDOFF.md](NEXT_CHAT_HANDOFF.md) — 현재 체크포인트와 바로 다음 단계
3. [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md) — 상세 상태와 승인 경계

과거 문서를 처음부터 전부 읽지 말고, 작업에 직접 필요한 경우에만 [Docs Hub](docs/README.md)를 통해 reference, contracts, guides, archive history를 찾아보세요. 현재 다음 단계와 승인 경계는 `NEXT_CHAT_HANDOFF.md`만 기준으로 판단합니다.

문서를 읽은 뒤 완료된 v377 source·private environment·local recovery migration·실제 Naver 메일 인증과 로그인을 다시 전면 감사하지 말고 `diagnose-v377-brevo-delivery-finalize`를 이어서 진행해주세요. local DB는 v377이고 local Brevo E2E는 성공했으며 Neon은 untouched v295입니다. 실제 메일은 도착하고 token 인증·로그인도 성공했지만 해당 outbox 행이 provider completion ambiguity 때문에 `delivery_outcome_unknown`으로 안전 종료된 원인을 secret·수신자·token을 출력하지 않는 focused 범위에서 진단하세요. 기존 marker/evidence 삭제·덮어쓰기, 중복 메일·자동 retry, DB reset·seed·restore·stamp·actual downgrade와 남은 공개 gate 우회는 하지 마세요.
