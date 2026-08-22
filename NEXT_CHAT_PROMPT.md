# Upgrade RPG 다음 채팅 시작 안내

프로젝트 루트에서 다음 문서를 순서대로 읽고 이어서 작업해주세요.

1. [AGENTS.md](AGENTS.md) — 계속 지켜야 할 규칙
2. [NEXT_CHAT_HANDOFF.md](NEXT_CHAT_HANDOFF.md) — 현재 체크포인트와 바로 다음 단계
3. [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md) — 상세 상태와 승인 경계

과거 문서를 처음부터 전부 읽지 말고, 작업에 직접 필요한 경우에만 [Docs Hub](docs/README.md)를 통해 reference, contracts, guides, archive history를 찾아보세요. 현재 다음 단계와 승인 경계는 `NEXT_CHAT_HANDOFF.md`만 기준으로 판단합니다.

문서를 읽은 뒤 완료된 v377 source-prepared 구현을 다시 전면 감사하거나 장황하게 요약하지 말고, 이미 승인된 `prepare-v377-private-email-environment`를 즉시 이어서 진행해주세요. clean pushed source SHA에서 ignored dotenv·기존 DB security artifact의 private ACL과 email/abuse secret 준비 → 고정 synthetic DB 왕복 1회 → 같은 보고서를 강제한 local/Neon fresh backup·exact v377 apply → Brevo/Render 설정 → 실제 이메일 end-to-end 확인 순서를 유지하세요. 이미 승인된 범위를 다시 묻지 말고, Brevo 가입·발신자 소유 인증·API key 입력처럼 Codex가 대신할 수 없는 사용자 행동만 한 번에 모아 요청하세요. DB reset·seed·restore·stamp·actual downgrade·자동 retry와 남은 공개 gate 우회는 하지 마세요.
