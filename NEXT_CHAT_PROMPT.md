# Upgrade RPG 다음 채팅 시작 안내

프로젝트 루트에서 다음 문서를 순서대로 읽고 이어서 작업해주세요.

1. [AGENTS.md](AGENTS.md) — 계속 지켜야 할 규칙
2. [NEXT_CHAT_HANDOFF.md](NEXT_CHAT_HANDOFF.md) — 현재 체크포인트와 바로 다음 단계
3. [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md) — 상세 상태와 승인 경계

과거 문서를 처음부터 전부 읽지 말고, 작업에 직접 필요한 경우에만 [Docs Hub](docs/README.md)를 통해 reference, contracts, guides, archive history를 찾아보세요. 현재 다음 단계와 승인 경계는 `NEXT_CHAT_HANDOFF.md`만 기준으로 판단합니다.

문서를 읽은 뒤 완료된 v377 source 구현이나 private environment 준비를 다시 전면 감사하지 말고 `prepare-v377-stale-evidence-recovery`를 이어서 진행해주세요. `8db9bcb`의 isolated 왕복·local backup은 새 canonicalization SHA에 stale이고, local apply는 Alembic 전에 안전 중단되어 report 없이 marker가 남았으며 DB는 v295입니다. 기존 action 재실행이나 marker/evidence 삭제·덮어쓰기 대신 새 namespace·artifact·confirmation을 쓰는 recovery 계약을 먼저 준비하고 exact 실행 범위를 별도 승인받으세요. Neon은 untouched로 유지합니다. DB reset·seed·restore·stamp·actual downgrade·자동 retry와 남은 공개 gate 우회는 하지 마세요.
