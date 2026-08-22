# Upgrade RPG 다음 채팅 시작 안내

프로젝트 루트에서 다음 문서를 순서대로 읽고 이어서 작업해주세요.

1. [AGENTS.md](AGENTS.md) — 계속 지켜야 할 규칙
2. [NEXT_CHAT_HANDOFF.md](NEXT_CHAT_HANDOFF.md) — 현재 체크포인트와 바로 다음 단계
3. [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md) — 상세 상태와 승인 경계

과거 문서를 처음부터 전부 읽지 말고, 작업에 직접 필요한 경우에만 [Docs Hub](docs/README.md)를 통해 reference, contracts, guides, archive history를 찾아보세요. 현재 다음 단계와 승인 경계는 `NEXT_CHAT_HANDOFF.md`만 기준으로 판단합니다.

문서를 읽은 뒤 완료된 v377 source·private environment·local recovery migration을 다시 전면 감사하지 말고 `configure-v377-local-brevo-provider`를 이어서 진행해주세요. local DB는 v377이고 인증 요청 보호 503과 이메일 없는 기존 계정 로그인 차단은 해결됐으며 Neon은 untouched v295입니다. 기호가 직접 해야 하는 Brevo 계정·sender 소유 확인·privacy 설정·전용 API key 준비를 한 번에 안내한 뒤 key와 발신 이메일을 값 출력 없이 local dotenv에 넣고 실제 테스트 메일과 가입→인증→로그인을 확인하세요. 기존 marker/evidence 삭제·덮어쓰기, DB reset·seed·restore·stamp·actual downgrade·자동 retry와 남은 공개 gate 우회는 하지 마세요.
