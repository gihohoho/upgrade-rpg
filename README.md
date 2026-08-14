# Upgrade RPG

웹 기반 방치형 Upgrade RPG 프로젝트입니다. 현재 공개 버전은 v351이며, 로컬 checkpoint는 v373 dependency·문서 탐색 준비 단계입니다. Alembic source head는 v371이고 DB는 계속 v295입니다.

## 새 작업 시작

다음 세 문서만 먼저 읽습니다.

1. [AGENTS.md](AGENTS.md)
2. [NEXT_CHAT_HANDOFF.md](NEXT_CHAT_HANDOFF.md)
3. [현재 상태](docs/current/CURRENT_STATUS.md)

전체 문서 위치는 [Docs Hub](docs/README.md), 폴더 운영 규칙은 [Documentation System](docs/DOCUMENTATION_SYSTEM.md)을 봅니다.

## 핵심 폴더

- `index.html`, `admin.html`, `src/`: legacy 게임과 관리자 화면
- `backend/`: FastAPI, SQLAlchemy, Alembic, production image
- `frontend/vue-app/`: Vue read-only 전환 실험
- `deploy/`: 배포 계약, 설정 예시, 정제된 증거
- `docs/current/`: 지금 판단과 승인에 필요한 문서
- `docs/reference/`: 주제별 장기 기술 자료
- `docs/generated/`: 도구가 생성하는 보고서
- `docs/contracts/`, `docs/guides/`: API 계약과 실행 절차
- `docs/archive/history/`: 완료된 단계의 검색용 통합 역사
- `tools/`: checker, report, smoke, maintenance

## 현재 고정값

```txt
GHCR: ghcr.io/gihohoho/upgrade-rpg-backend
target: linux/amd64
database: Neon PostgreSQL 16 Singapore
hosting: Render Free Web Service + Static Site
public backend/static: v351 Live
local checkpoint: v373 / migration source v371 / DB still v295
```

로컬 서버를 실행하거나 배포하기 전에는 관련 guide와 현재 승인 경계를 먼저 확인합니다.
