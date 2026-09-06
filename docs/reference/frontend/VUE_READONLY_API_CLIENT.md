# Vue API client 경계

게임·계정 API는 TypeScript client가 맡고, 기존 관리자 GET client는 호환 경계를 유지합니다. v396에서 사용처가 없는 `gameReadOnlyApi.js`를 삭제했으며 실제 호출을 맡는 `gameApi.ts`는 그대로 사용합니다. API 경로·응답 계약의 기준은 [API Response Contract](../../contracts/API_RESPONSE_CONTRACT.md), 전체 전환 범위는 [Vue 전환 계획](VUE_FASTAPI_DB_TRANSITION_PLAN.md)입니다.

## 현재 책임

| 모듈 | 책임 |
|---|---|
| `http.ts` | typed 요청, Bearer 전달, 응답 envelope와 HTTP 오류 |
| `gameApi.ts` | 선택 캐릭터 load GET, 직렬 queue가 호출하는 save POST |
| `authApi.ts`·`accountApi.ts` | 로그인·이메일 흐름, 계정별 캐릭터 슬롯과 master-data GET |
| `healthReadOnlyApi.js` | `/health` 상태 GET |
| `adminReadOnlyApi.js` | `/admin/requirements`·overview·master-data·이력 GET |
| `adminPreviewApi.ts` | `dryRun: true`로 고정된 Preview POST 5종 |

Vue component는 API 결과를 store의 상태로 표시합니다. 공통 API 요청에 임의의 dev key나 비밀번호 header를 넣지 않습니다.

## 게임 저장과 수명주기

선택한 계정·`character-N`·32자리 `accountCharacterId`가 일치할 때만 server snapshot을 적용합니다. 신규 빈 snapshot은 기본 상태로 시작하며 서버가 정상 load의 기준입니다.

`POST /game/save`는 60초 자동 저장·수동 저장·전환 전 최종 저장이 공유하는 단일 queue에서 호출합니다. 각 요청은 호출 시점 snapshot과 identity를 복제합니다. v396은 reset/reload 이전 context의 늦은 응답을 취소하고 409·401·403 뒤 이미 대기한 요청과 후속 POST도 차단합니다. 명시적 context 복구 뒤에는 저장할 수 있고, network/5xx는 같은 context에서 재시도할 수 있습니다.

현재 `saveVersion`은 snapshot 형식 버전이며 backend CAS는 미구현입니다. v397의 Vue local fallback은 요청 전 snapshot과 pending을 함께 기록하고, 재진입 시 사용자 선택 뒤 공통 queue로 재전송하거나 서버본을 적용합니다. 자세한 키·백업·실패 경계는 [계정·캐릭터 저장 계약](../../current/ACCOUNT_AUTH_AND_CHARACTER_SLOTS.md)을 따릅니다.

## 관리자 GET·Preview

관리자 route/store는 로그인 계정의 `isAdmin=true`와 Bearer 인증을 요구합니다. 401/403 응답이면 관리자 화면을 닫고 인증 gate로 돌아갑니다.

상세·관계 wrapper의 `rowId`는 backend query의 `id`로 변환합니다. 카탈로그는 검색·필터·정렬·페이지네이션을 지원하고 detail/relations는 서버가 내려준 field·relation schema를 표시합니다.

Preview는 생성·수정·일반 rollback·생성 삭제·복원 요청만 허용합니다. store는 최신 Preview와 SHA-256, 응답의 `confirmTextRequired`를 확인 modal에 사용합니다. 확인 문구·비밀번호·dev key는 Preview 요청에 보내지 않습니다. 실제 관리자 Apply/write·재인증 request·DB write는 연결하지 않았습니다.

## 공통 UI와 오류

관리자 값 표시와 오류 문구는 공통 helper를 재사용합니다. 게임·계정 modal은 `useModalAccessibility.ts`에서 focus trap·배경 inert·Escape·초점 복귀를 공유합니다. 관리자 Apply modal의 독립 확인 gate는 유지합니다. API 실패는 해당 panel의 오류로 표시하고 게임 shell 전체를 빈 화면으로 만들지 않습니다.

## 실행과 검증

실행 위치·Python `.venv` 상태·새 설치 여부를 포함한 로컬 준비 절차는 [루트 README](../../../README.md)의 한 곳에서 관리합니다. Vue/npm 위치는 `frontend/vue-app`이며 Python 가상환경은 필요 없습니다.

Vue 회귀 묶음은 `tools/run_smoke_vue_shell.sh`, API 경로 보고서는 [Backend Route Map](../../generated/BACKEND_ROUTE_MAP.md)을 사용합니다. 현재 checkpoint의 실제 실행 결과는 [Current Status](../../current/CURRENT_STATUS.md)를 따릅니다.

v271~v275의 GET 전용 도입과 v272 health panel은 초기 구현 이력입니다. 현재 게임 save와 관리자 Preview 범위에 과거의 GET 전용 제한을 적용하지 않습니다.
