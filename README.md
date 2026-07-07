# Upgrade RPG

현재 프로젝트는 아직 Vue가 아니라 **index.html + JS + CSS 기반 RPG 게임**입니다.
기존 게임을 정상 작동 상태로 유지하면서, FastAPI + PostgreSQL 백엔드를 단계적으로 붙이고 있습니다.

## 새 채팅 인수인계

새 채팅에서 이어갈 때는 이 파일을 먼저 참고하세요.

```txt
NEXT_CHAT_HANDOFF.md
```

그다음 현재 상태와 다음 단계를 보려면:

```txt
docs/CURRENT_STATUS.md
docs/NEXT_STEPS.md
docs/README.md
```

## 현재 안정 버전

- 최신 안정 버전: **v147: admin owner code relation tools**

v147은 v144의 조합 관계 필드 안전 편집 위에 `dropTables.owner_code` 안전 편집을 추가한 버전입니다. owner_type이 boss면 bosses 목록, field면 fieldZones 목록에서만 owner_code를 선택하게 하고, 백엔드가 preview/apply 단계에서 실제 대상 존재 여부를 다시 검사합니다. owner_type을 바꾸면 owner_code 후보 목록도 자동 전환됩니다.

DB schema, seed 데이터, localStorage 저장 구조는 변경하지 않았습니다.

## 백엔드 실행

```bash
# 위치: backend 폴더 + 가상환경 activate 상태
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

## smoke test

핵심 검사:

```bash
# 위치: 프로젝트 루트
bash tools/run_smoke_core.sh
```

전체 검사:

```bash
# 위치: 프로젝트 루트
bash tools/run_smoke_all.sh
```

## 관리자 페이지

게임 화면에서:

```txt
SAVE DATA → admin → 관리자 페이지 열기
```

관리자 실제 쓰기 기능은 로컬 개발용 dev key가 필요합니다.

```txt
local-admin-dev-key
```
