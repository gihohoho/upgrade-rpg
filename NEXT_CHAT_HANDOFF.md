# Upgrade RPG Codex handoff — v373

새 채팅은 루트 [AGENTS.md](AGENTS.md)를 먼저 읽고 이 문서를 이어서 사용합니다. 더 자세한 근거는 [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)에서 확인합니다.

```txt
latest: v373.email-validator-linux-locks-obsidian-ready
strict result: email-validator-linux-locks-obsidian-ready
next safe stage: owner-review-v371-migration-source-and-approve-isolated-roundtrip
source head: v371_email_identity_lifecycle
local/Neon DB current: v295_initial_schema
public backend/static: v351 Live
```

## 이번 체크포인트

- v370 계정 인증·8개 캐릭터 슬롯·관리자 회원 관리 위에 v371 이메일 인증, 아이디 찾기, 비밀번호 재설정과 계정 삭제 source를 준비했습니다.
- v371 migration source는 준비됐지만 local/Neon DB에는 적용하지 않았습니다.
- 승인된 `email-validator==2.3.0`과 `dnspython==2.8.0`을 backend `.venv`, Linux runtime/musllinux/dev lock과 GHCR 재현성 해시에 반영했습니다.
- Brevo HTTPS mail provider 코드와 게임 스타일 HTML/plaintext template은 준비됐지만 Brevo 계정·sender·API key·secret·실제 메일은 설정하지 않았습니다.
- owner bootstrap은 별도 one-shot입니다. 실제 실행하지 않았고 성공 전 이메일 인증을 요구합니다.
- source-prepared 즉시 수정 blocker는 없습니다. 공개 회원가입은 rate limit, mail queue/timing, raw body cap, 미인증 계정 회수, server session/revoke, save CAS, CSP/XSS·개인정보 정책이 남아 차단 상태입니다.
- 설치된 Obsidian 1.13.7에 저장소 루트를 `Upgrade RPG` local vault로 등록하고 ignored 설정과 표준 Markdown 링크망을 준비했습니다. 프로젝트에는 Obsidian plugin dependency가 없습니다.
- Linux lock check·`pip check`, packaging/강제 import-failure 503, v371 migration/owner와 v370 auth/admin 회귀, GHCR 재현성, compileall·blocking-I/O, 문서 구조와 전체 core smoke가 PASS했습니다.

## 바로 할 일

1. v371 migration source와 dependency/lock 변경을 검토합니다.
2. 기호의 별도 exact-SHA 승인 전에는 isolated PostgreSQL upgrade→downgrade→upgrade도 실행하지 않습니다.
3. isolated 왕복이 승인·검증돼도 local/Neon migration apply는 다시 별도 승인으로 남깁니다.
4. Brevo 설정·실제 메일·owner bootstrap·공개 배포도 각각 분리된 승인 단위입니다.

## 안전 경계

- 실제 secret/token/password를 출력·문서화·commit하지 않습니다.
- local/Neon migration과 어떤 DB write도 실행하지 않았으며, Brevo 설정/메일, owner bootstrap, GHCR/Render 배포는 각각 별도 승인입니다.
- 공개 frontend/backend는 v351이며 v370/v371 로컬 기능을 아직 배포하지 않았습니다.
- 사용자 변경 `src/styles/style.css`가 남아 있으면 건드리거나 stage하지 않습니다.

## 이번 문서 정리 결과

- 최종 Markdown을 243개에서 95개로, `docs/current`의 실제 현재 문서를 11개로 줄였습니다.
- 문서 수·current 예산·entry 크기·exact duplicate·obsolete 경로·활성 링크·131개 archive 원본 경로 smoke와 전체 core smoke가 PASS했습니다.
- 현재 판단: `docs/current/`
- 장기 기술 자료: `docs/reference/`
- 자동 생성 보고서: `docs/generated/`
- API 계약: `docs/contracts/`
- 실행 안내: `docs/guides/`
- 완료된 상세 역사: `docs/archive/history/`
- 새 채팅은 [AGENTS.md](AGENTS.md) → 이 문서 → [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)만 먼저 읽습니다.
- 매 작업 종료 시 위 핵심 3문서와 관련 Markdown을 함께 마감 점검하는 규칙을 장기 규칙과 구조 smoke에 반영했습니다.
- Obsidian에서는 저장소 루트를 vault로 사용하고, `.venv`·`node_modules`·build/backup/secret 경로는 local 검색에서 제외합니다. 일괄 frontmatter·tag와 community plugin은 사용하지 않습니다.

문서 체계는 [Documentation System](docs/DOCUMENTATION_SYSTEM.md), 전체 색인은 [Docs Hub](docs/README.md)가 기준입니다.
