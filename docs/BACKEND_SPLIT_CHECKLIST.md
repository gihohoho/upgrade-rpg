# 백엔드 분리 준비 체크리스트

## 1순위. 상태 분리

상태: 완료

완료된 내용:

- `gameState.server` 추가
- `gameState.client` 추가
- `gameState.runtime` 추가
- 기존 전역 변수 호환 유지
- 저장/불러오기용 헬퍼 추가

확인할 것:

- 게임 시작 가능
- 저장/불러오기 가능
- 필드 이동 가능
- 보스 소환 가능
- 아이템 장착/해제 가능
- 강화 가능

---

## 2순위. bosses.js 역할 분리

상태: 1차 완료

완료된 내용:

- 아이콘 유틸 분리: `src/utils/icon-utils.js`
- 고티어 보스 생성 공식 분리: `src/data/boss-factories.js`
- 보스 원본 데이터 파일 축소: `src/data/bosses.js`
- 심연의 편린 특수 옵션 규칙 분리: `src/rules/abyss-fragment-rules.js`
- 보스 표시 후처리 분리: `src/rules/boss-display-rules.js`
- 드랍률 보정/최초 보너스 규칙 분리: `src/rules/boss-drop-rules.js`
- 후처리 실행 파일 추가: `src/data/boss-bootstrap.js`

남은 작업:

- [ ] 아이템 원본을 `items.js` 또는 DB seed 형태로 완전 분리
- [ ] 드랍 테이블을 `drop-rules.js` 또는 DB seed 형태로 완전 분리
- [ ] `boss-drop-rules.js`의 전역 UI/player 의존 제거

---

## 3순위. 캐릭터별 스킬 구조 준비

상태: 1차 완료

완료된 내용:

- `src/data/skills.js` 추가
- 현재 기본 캐릭터 `weapon_master` 등록
- 현재 스킬 8개를 스킬 마스터 데이터로 분리
- Q/SQ, W/SW 각성 정보를 스킬 데이터 내부로 이동
- 스킬강화권 매핑을 `skillBookMasterData`로 분리
- `player.currentCharacterId`, `player.ownedCharacterIds`, `player.userCharacters` 구조 추가
- 기존 코드 호환용 `player.skills` 유지
- `renderSkills()`가 중앙 스킬 데이터 기반으로 스킬 UI를 그리도록 변경
- `item-system.js`의 스킬강화권 사용 로직이 중앙 스킬 데이터/현재 캐릭터 스킬을 참조하도록 변경
- `combat-system.js`가 `player.skills` 대신 현재 캐릭터 스킬 헬퍼를 우선 사용하도록 변경

남은 작업:

- [ ] 전투 공식 전체를 `skillMasterData` 기반으로 완전 데이터화
- [ ] 스킬 타입별 처리기 분리: 패시브/확률딜/버프/진각성
- [ ] 관리자 페이지에서 스킬 발동률/계수/쿨타임 수정 가능하게 DB화

---

## 4순위. 시스템 함수와 UI 분리

상태: 3차 완료

완료된 내용:

- `src/systems/action-result-system.js` 추가
- `playerAttack()`이 공격 결과 객체를 생성하도록 변경
- 스킬 발동 내역/총 피해량/대상/처치 여부를 결과 객체에 저장
- 스킬 데미지 텍스트를 즉시 출력하지 않고 결과 객체의 `effects`로 전달
- `actionReinforce(times)`가 강화 결과 객체를 생성하도록 변경
- 강화 로그/강화 결과창/UI 갱신 요청을 결과 객체로 모은 뒤 `applyActionResultUi()`에서 처리
- 보스/필드 처치, 드랍, 골드/성장 보상을 `combat.kill` 결과 객체로 1차 정리

남은 작업:

- [x] `killEnemy()`의 보스 처치/드랍/필드 보상 로직 결과 객체화
- [x] `actionEquipDirect()` / `actionUnequipDirect()` 결과 객체화
- [x] 스킬강화권 사용 결과 객체화
- [x] 보스 소환 결과 객체화
- [ ] 보관함/휴지통/우편 이동 결과 객체화
- [ ] 시스템 함수 내부의 직접 UI 호출 추가 축소

완료 기준:

- 핵심 함수가 `renderUI()`에 직접 의존하지 않는다.
- 핵심 함수가 `document.getElementById()`에 직접 의존하지 않는다.
- 결과 객체만으로 UI를 다시 그릴 수 있다.

---

### 4순위 2차 완료

- `killEnemy()` 중심으로 처치/드랍/보상 결과를 객체화했습니다.

### 4순위 3차 완료

- 장착/해제, 스킬강화권 사용, 보스 소환 결과를 객체화했습니다.
- 남은 4순위 후속 후보: 보관함/휴지통/우편 이동, 보스 제거, 토글 명령어 결과 객체화.

## 5순위. API 응답 형태 확정

상태: 완료

완료된 내용:

- `docs/API_RESPONSE_CONTRACT.md` 추가
- `src/api/api-response-contract.js` 추가
- `src/api/API_PLAN.md`를 확정 응답 형태 기준으로 갱신
- 저장/불러오기 응답 형태 정리
- 마스터 데이터 응답 형태 정리
- 공격/처치/보스 소환 응답 형태 정리
- 장착/해제/강화 응답 형태 정리
- 스킬강화권 사용 응답 형태 정리
- 관리자 변경 응답 형태 정리
- 실패 응답과 공통 에러 코드 정리
- `tools/smoke_api_response_contract.js` 추가

완료 기준:

- FastAPI 구현 전에 프론트가 예상 응답 형태를 알 수 있다.
- 관리자 페이지와 유저 게임 화면이 같은 마스터 데이터를 사용할 수 있다.
- 현재 Action Result 구조와 FastAPI 응답 형태의 연결 기준이 있다.

브라우저 확인:

- 이번 5순위는 문서/계약/미사용 헬퍼 추가 작업이라 브라우저에서 따로 확인할 항목은 없습니다.



## v075 추가 완료 항목

```txt
[x] 관리자 페이지 요구사항 V1 문서화
[x] PostgreSQL DB 설계 초안 작성
[x] FastAPI backend/ 프로젝트 뼈대 생성
[x] 공통 API 응답 헬퍼 작성
[x] SQLAlchemy 모델 초안 작성
[x] API 라우터 stub 작성
[x] backend 구조 smoke 검사 추가
```


## v078 진행 상태

- [x] seed JSON을 PostgreSQL에 넣기 위한 import 스크립트 추가
- [x] 로컬 DB reset/create/seed/verify 명령어 정리
- [x] seed import 문서 추가
- [x] 큰 숫자 HP/골드 저장을 위한 DB 타입 보정

다음 단계:

- [ ] `/game/master-data` API가 DB에서 실제 마스터 데이터를 읽도록 구현

