# Upgrade RPG 다음 채팅 시작 안내

프로젝트 루트에서 다음 문서를 순서대로 읽고 이어서 작업해주세요.

1. [AGENTS.md](AGENTS.md) — 계속 지켜야 할 규칙
2. [NEXT_CHAT_HANDOFF.md](NEXT_CHAT_HANDOFF.md) — 현재 체크포인트와 바로 다음 단계
3. [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md) — 상세 상태와 승인 경계

과거 문서를 처음부터 전부 읽지 말고, 작업에 직접 필요한 경우에만 [Docs Hub](docs/README.md)를 통해 reference, contracts, guides, archive history를 찾아보세요. 현재 다음 단계와 승인 경계는 `NEXT_CHAT_HANDOFF.md`만 기준으로 판단합니다.

문서를 읽은 뒤 완료된 v377 source·private environment·local/Neon migration·Brevo E2E·GitHub/GHCR·Render backend 배포, v378 static 배포와 v379~v391 Vue 기반·인증·관리자 경계·typed game domain·마을/HUD·필드·보스·인벤토리/장비·보관함/휴지통·스킬/강화·상점/설정 UI를 다시 전면 감사하거나 재실행하지 말고 `migrate-vue-game-combat-runtime-foundation`을 이어서 진행해주세요. Docker와 로컬 로그인은 기호가 정상 동작을 직접 확인했으므로 반복하지 마세요. 다음 단계에서는 typed 전투 계산을 사용하는 client runtime controller와 timer lifecycle만 분리하고, server snapshot load/save·자동 저장·Gold/아이템 보상·난수 드랍은 함께 연결하지 마세요. 실제 스킬 사용·강화·재료 소비·아이템 이동/복구/삭제·상점 구매/판매·설정 영구 저장, Apply endpoint·재인증 request·dev key header·DB write와 production 관리자 복구는 각각 exact 범위를 별도 승인받기 전에는 실행하지 마세요. 기존 marker/evidence 삭제·덮어쓰기, 자동 retry, DB reset·seed·restore·stamp·actual downgrade와 남은 공개 gate 우회는 하지 마세요.
