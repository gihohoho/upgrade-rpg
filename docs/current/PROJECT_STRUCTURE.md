# Project Structure — v315

```txt
.
├── AGENTS.md                              # Codex 저장소 규칙
├── NEXT_CHAT_PROMPT.md                    # Codex 새 채팅에 붙여넣을 프롬프트
├── NEXT_CHAT_HANDOFF.md                   # 현재 상태 요약
├── index.html / admin.html / src/         # legacy 게임·관리자
├── frontend/vue-app/                      # Vue GET read-only 앱
├── backend/
│   ├── .venv/                             # 로컬 전용, ZIP/Git 제외
│   ├── Dockerfile                         # 로컬 호환
│   └── Dockerfile.production              # exact base digest/non-root
├── deploy/
│   ├── backend-image-ghcr-policy.example.json
│   ├── docker-compose.production.yml
│   ├── production.env.example
│   ├── review/                            # 완료된 정적 review 증거
│   └── isolated-validation/
├── docs/
│   ├── current/                           # 현재 판단
│   ├── handoff/                           # 인수인계 mirror
│   ├── contracts/
│   └── archive/                           # 과거 단계 기록
└── tools/
    ├── check_codex_handoff_readiness.py
    └── smoke/
```

legacy 경로는 Vue 이식 전까지 유지합니다. 현재 배포 repository는 `ghcr.io/gihohoho/upgrade-rpg-backend`입니다.
