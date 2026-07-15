# Project Structure — v313

```txt
.
├── index.html
├── admin.html
├── src/                                   # legacy JS/CSS
├── frontend/vue-app/                      # Vue GET read-only 앱
├── backend/                               # FastAPI/SQLAlchemy/Alembic
├── deploy/
│   ├── docker-compose.production.yml      # backend-only review template
│   ├── production.env.example
│   ├── production-capacity-plan.example.json
│   ├── production-architecture-selection.example.json
│   ├── backend-image-source-digest-policy.example.json
│   ├── review/
│   │   └── production-compose-config-render-v312.json
│   ├── reverse-proxy/README.md
│   ├── isolated-validation/README.md
│   └── secrets/README.md
├── tools/
│   ├── check_production_managed_postgres_reverse_proxy_selection.py
│   ├── render_production_compose_config.py
│   ├── check_backend_image_source_digest_policy.py
│   └── smoke/
├── docs/
│   ├── current/
│   ├── archive/
│   ├── contracts/
│   └── handoff/
├── NEXT_CHAT_PROMPT.md
└── NEXT_CHAT_HANDOFF.md
```

## 유지 경계

- legacy 게임/관리자/`src/`는 Vue 이식 전까지 이동하지 않음
- Vue는 GET read-only까지만 연결
- Preview/Apply/write/인증과 게임 콘텐츠 개발 보류
- Alembic revision은 `v295_initial_schema` 유지
- 실제 DB/env/secret/Docker resource는 승인 없이 변경 금지

## production 구조

- production Compose: backend service 하나
- 관리형 PostgreSQL은 Compose 외부 provider endpoint
- reverse proxy는 external edge network에서 backend `8000` 접근
- backend image는 exact digest 요구
- provider CA만 Compose secret mount
- actual deployment 파일은 Git/ZIP/build context 제외

## 현재 검사

```txt
tools/check_production_secrets_tls_container_static.py
tools/check_production_capacity_tls_network_plan.py
tools/check_production_managed_postgres_reverse_proxy_selection.py
tools/render_production_compose_config.py
tools/check_backend_image_source_digest_policy.py
```

config render는 기호 PC에서 완료됐습니다. 현재 새 checker는 repository 파일만 읽으며 pull/build/push를 호출하지 않습니다.
