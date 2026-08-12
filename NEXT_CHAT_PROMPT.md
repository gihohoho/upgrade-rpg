# Upgrade RPG 다음 채팅 시작 안내

프로젝트 루트에서 다음 문서를 순서대로 읽고 이어서 작업해주세요.

1. `AGENTS.md` — 계속 지켜야 할 규칙
2. `NEXT_CHAT_HANDOFF.md` — 현재 체크포인트와 바로 다음 단계
3. `docs/current/CURRENT_STATUS.md` — 상세 상태와 승인 경계

과거 문서를 처음부터 전부 읽지 말고, 작업에 직접 필요한 경우에만 `docs/README.md`를 통해 `docs/reference/`, `docs/contracts/`, `docs/guides/`, `docs/archive/history/`를 찾아보세요.

현재 다음 단계는 `email-validator==2.3.0` 설치·Linux lock 갱신 승인입니다. 승인 전에는 설치, migration, DB write, Brevo 호출, owner bootstrap, 배포를 실행하지 마세요.
