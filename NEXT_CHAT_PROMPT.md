# Upgrade RPG 다음 채팅 시작 안내

프로젝트 루트에서 다음 문서를 순서대로 읽고 이어서 작업해주세요.

1. [AGENTS.md](AGENTS.md) — 계속 지켜야 할 규칙
2. [NEXT_CHAT_HANDOFF.md](NEXT_CHAT_HANDOFF.md) — 현재 체크포인트와 바로 다음 단계
3. [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md) — 상세 상태와 승인 경계

과거 문서를 처음부터 전부 읽지 말고, 작업에 직접 필요한 경우에만 [Docs Hub](docs/README.md)를 통해 reference, contracts, guides, archive history를 찾아보세요. 현재 다음 단계와 승인 경계는 `NEXT_CHAT_HANDOFF.md`만 기준으로 판단합니다.

문서를 읽은 뒤 완료된 v377 source·private environment·local migration·Brevo E2E와 provider 진단을 다시 전면 감사하지 말고 `execute-v377-recovery2-roundtrip-and-neon`을 이어서 진행해주세요. clean pushed exact SHA에서 새 `recovery2` synthetic 왕복을 1회 완료한 뒤 같은 SHA와 report로 untouched Neon의 fresh backup·exact v377 apply를 각각 1회 실행하세요. 그 다음에만 fresh GitHub publish lifecycle과 새 signed digest, Render key-only 준비·단일 backend deploy, 같은 exact source의 static deploy 순서로 진행하세요. 기존 marker/evidence 삭제·덮어쓰기, 자동 retry, DB reset·seed·restore·stamp·actual downgrade와 남은 공개 gate 우회는 하지 마세요.
