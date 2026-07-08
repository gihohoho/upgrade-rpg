# Upgrade RPG

현재 안정 버전: **v177 create apply skills/dropTables**

새 채팅 인수인계 ZIP: **rpg_v177_skills_droptables_create_apply_ready.zip**

현재 프로젝트는 아직 Vue가 아니라 `index.html + JS + CSS` 기반 RPG 게임입니다. 기존 게임 동작을 유지하면서 FastAPI + PostgreSQL + 관리자 페이지 구조로 단계적으로 분리 중입니다.

## 현재 핵심 상태

- 게임 localStorage 저장 유지: `idleRpgSaveV22`
- DB save snapshot dual write 유지
- master-data PostgreSQL → FastAPI → 브라우저 연결 유지
- 백엔드 실패 시 static JS fallback 유지
- 관리자 페이지 `admin.html` 분리 유지
- 관리자 edit/create/delete/restore 제한 기능 유지
- 관리자 sidebar / sticky header / 접기·펼치기 shell 유지
- 접힌 탭 공통 CSS 보정 완료
- `fieldZones` 신규 row create apply 제한 오픈 완료
- `bosses` 신규 row create apply 제한 오픈 완료
- `skills`, `dropTables` 신규 row create apply 제한 오픈 완료

## 새 채팅에서 먼저 볼 파일

- `NEXT_CHAT_HANDOFF.md`
- `NEXT_CHAT_PROMPT.md`
- `docs/CURRENT_STATUS.md`
- `docs/NEXT_STEPS.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/README.md`

## smoke 실행

```bash
위치: 프로젝트 루트
bash tools/run_smoke_core.sh
```

```bash
위치: 프로젝트 루트
bash tools/run_smoke_all.sh
```

## 다음 추천 단계

`skills`, `dropTables` create apply가 열렸으므로 다음은 실제 브라우저에서 스킬/드랍 테이블 생성·삭제·복원 흐름을 한 번 확인하는 것이 안전합니다. `itemTemplates`, `dropTableItems`는 아직 신규 생성 apply를 열지 않는 것이 좋습니다.

## DB / env

- DB reset / seed 필요 없음.
- DB schema 변경 없음.
- `.env`, `.gitignore` 변경 없음.
- 이 ZIP에는 `.env`, `.gitignore`를 포함하지 않았습니다.
