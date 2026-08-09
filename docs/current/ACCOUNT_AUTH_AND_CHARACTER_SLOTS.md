# 계정 인증·캐릭터 슬롯·회원 관리 — v370

```txt
latest: v370.account-auth-character-slots-admin-management-local-ready
strict result: account-auth-character-slots-admin-management-local-ready
next safe stage: owner-create-local-account-bootstrap-admin-and-verify-authenticated-multicharacter-flow
public Render: backend/static 모두 계속 v351
```

## 이번 단계의 목표

게임을 처음 열면 바로 플레이 화면을 시작하지 않고 다음 순서로 진입합니다.

```txt
로그인 또는 회원가입
  → 계정의 캐릭터 슬롯 8개 조회
  → 기존 캐릭터 선택 또는 빈 슬롯에 캐릭터 생성
  → 선택한 캐릭터의 저장 데이터만 로드
  → 게임 시작
```

소셜 로그인은 나중에 추가할 수 있도록 고려하되, 이번 단계에는 OAuth 공급자,
버튼, 외부 SDK와 사용하지 않는 설정을 만들지 않습니다.

## 데이터 구조

이번 MVP는 새 테이블과 Alembic revision을 만들지 않습니다.

- `users`: 아이디, bcrypt 비밀번호 해시, 활성/정지, 관리자 여부
- `user_profiles`: 기존 계정 프로필 1:1 행
- `user_save_snapshots`: 계정별 캐릭터 슬롯과 전체 게임 저장
- `admin_change_logs`: 최초 관리자 지정과 회원 활성/정지 감사 기록
- `characters`: 검신 같은 선택 가능한 **캐릭터 종류 마스터 데이터**이며 계정 슬롯이 아님

한 계정의 슬롯은 DB에서 `character-1`부터 `character-8`까지 고정합니다. 각
`user_save_snapshots.summary_json.accountCharacter`에는 다음 안전 메타데이터만
보관합니다.

```json
{
  "id": "32자리 무작위 캐릭터 고유 ID",
  "slotIndex": 1,
  "name": "사용자가 정한 이름",
  "characterCode": "weapon_master",
  "createdAt": "UTC 시각"
}
```

슬롯 번호는 재사용될 수 있지만 캐릭터 고유 ID는 다시 만들 때마다 바뀝니다.
API 요청·응답에서는 이 `summary_json.accountCharacter.id` 값을
`accountCharacterId`라는 필드명으로 전달합니다.
서버는 저장·불러오기 때 현재 로그인 계정, `character-N` 슬롯 키, 캐릭터 고유
ID가 모두 일치해야만 요청을 허용합니다. 따라서 캐릭터를 삭제한 뒤 같은 슬롯에
다시 만들어도 이전 브라우저 캐시가 새 캐릭터에 자동 연결되지 않습니다.

기존 `UserCharacterSkill`, `UserEquipmentSlot`, `ItemInstance` 같은 정규화 초안
테이블은 같은 직업 캐릭터 여러 개를 구분할 수 없으므로 이번 단계에서 이중 쓰기하지
않습니다. 캐릭터 한 명은 기존 게임 전체 save snapshot 한 개를 소유합니다.

## 인증과 비밀번호

- 회원가입 아이디는 소문자 영문·숫자·밑줄의 4~24자 규칙으로 정규화합니다.
- 비밀번호는 최소 8자, 문자와 숫자를 각각 하나 이상 포함하고 UTF-8 72바이트를
  넘지 않아야 합니다.
- 비밀번호는 `bcrypt 5.0.0`으로만 해시하며 원문과 해시는 API, 관리자 화면,
  로그, 문서에 반환하지 않습니다.
- CPU 비용이 큰 bcrypt hash/verify는 FastAPI event loop가 아니라 worker
  thread에서 실행합니다.
- 로그인 성공 시 기존 `JWT_SECRET_KEY`로 HS256 서명한 24시간 access token을
  발급합니다. 서버는 알고리즘을 고정하고 서명, 종류, 발급 시각과 만료 시각을
  검사합니다.
- 로그인 유지가 꺼져 있으면 token은 `sessionStorage`, 사용자가 명시적으로 켜면
  `localStorage`에 저장합니다. 로그아웃은 클라이언트 token을 즉시 삭제합니다.
- 매 인증 요청마다 DB의 계정을 다시 읽으므로 관리자가 계정을 정지하면 이미 발급된
  token도 다음 요청부터 즉시 거절됩니다.
- 회원가입 요청으로 관리자 권한을 받을 수 없으며 항상 `is_admin=false`입니다.

서버 session/refresh token 테이블은 이번 MVP에 없습니다. 따라서 개별 기기 강제
로그아웃, token 목록과 원격 폐기, refresh rotation은 아직 제공하지 않습니다.
전체 token을 무효화해야 하면 `JWT_SECRET_KEY`를 회전하고 새 backend image를
배포해야 합니다.

## API 계약

공개 경로:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/game/master-data`
- health 경로

Bearer 로그인이 필요한 경로:

- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`
- `GET /api/v1/account/characters`
- `POST /api/v1/account/characters`
- `DELETE /api/v1/account/characters/{account_character_id}`
- `GET /api/v1/game/load`
- `GET /api/v1/game/save-slots`
- `POST /api/v1/game/save`

서비스가 `snapshot`, 슬롯 키와 캐릭터 고유 ID를 안정적으로 JSON 직렬화한 크기는
최대 2,000,000바이트이며 초과 시 `413`으로 닫힙니다. 이는 JSON 파싱 뒤의 저장
계약 제한이며, ASGI 계층에서 HTTP raw body를 파싱 전에 차단하는 제한은 공개 전
후속 보강 항목입니다. 클라이언트가 임의 `userId`를 보내 소유자를 선택할 수 없고,
항상 access token의 현재 계정 ID만 사용합니다.

관리자 회원 API:

- `GET /api/v1/account-admin/bootstrap-status`
- `POST /api/v1/account-admin/bootstrap`
- `GET /api/v1/account-admin/users`
- `GET /api/v1/account-admin/users/{user_id}`
- `POST /api/v1/account-admin/users/{user_id}/status-preview`
- `POST /api/v1/account-admin/users/{user_id}/status-apply`

`bootstrap-status`와 최초 관리자 지정은 로그인 계정만 사용할 수 있습니다. 최초
관리자 지정은 로그인 가능한 관리자가 한 명도 없을 때 현재 로그인 계정과 별도
`X-Admin-Dev-Key`가 모두 확인되어야 한 번만 실행됩니다. 기존 `local-dev`처럼
비밀번호 해시가 없는 과거 placeholder 계정은 로그인 가능한 관리자로 세지 않습니다.

회원 목록·상세·preview는 실제 관리자만 볼 수 있습니다. 상태 apply는 관리자
Bearer 권한에 더해 기존 dev key를 두 번째 방어선으로 유지하고, 정확한 확인 문구,
stale 상태, 본인 정지 금지, 마지막 로그인 가능 관리자 정지 금지를 검사한 뒤
`AdminChangeLog`와 같은 transaction에서 반영합니다. 관리자 API는 비밀번호 해시,
token, 전체 `snapshot_json`을 반환하지 않습니다.

## 서버 기준 저장·브라우저 복구와 캐릭터 전환

- 기존 단일 키 `idleRpgSaveV22`는 삭제하거나 자동 덮어쓰지 않고 명시적 가져오기
  원본으로만 보존합니다.
- 새 로컬 저장 키에는 계정 ID와 캐릭터 고유 ID를 모두 넣습니다.
- DB 저장 키는 캐릭터 고유 ID가 아니라 고정 슬롯 번호 `character-N`을 씁니다.
- 정상 load의 authoritative 원본은 서버 DB snapshot입니다. backend에 snapshot이 있으면
  그 내용을 사용합니다. 서로 다른 local이 남아 있으면 즉시 삭제하지 않고
  `${saveKey}.pre-backend-recovery`에 복구 백업을 만든 뒤 활성 local을 서버본으로
  교체합니다.
- backend snapshot이 비어 있을 때만 계정·캐릭터가 일치하는 local을 복구 원본으로
  사용하고, 게임을 시작한 뒤 같은 직렬 저장 큐에 넣어 서버에 저장합니다. 따라서 평상시
  local이 서버보다 우선한다는 정책이 아닙니다.
- 이전 backend 저장 실패로 해당 계정·캐릭터에 `pending-unsynced` marker가 있고 local도
  존재하면 자동 선택하지 않습니다. `이 기기 저장 사용`은 local을 불러 서버에 다시
  전송하고, `서버 저장 사용`은 local을 복구 백업한 뒤 서버본을 사용하며, 취소는 두
  원본과 marker를 그대로 보존하고 슬롯 화면으로 돌아갑니다.
- 자동 저장, 수동 저장, 캐릭터 전환·로그아웃 최종 저장은 모두 하나의 Promise 직렬 저장
  큐를 사용합니다. 각 요청은 호출 시점 snapshot과 계정·슬롯·캐릭터 ID를 고정해 앞선
  저장이 끝난 뒤 순서대로 실행합니다.
- 캐릭터 선택 뒤에만 게임 load, UI 초기화, 자동 저장 timer가 정확히 한 번 시작됩니다.
- 전환과 로그아웃은 runtime·전투·timer를 먼저 pause하고 기존 저장 큐와 마지막 저장을
  drain합니다. 성공한 뒤에만 선택 상태 또는 token을 정리하고 reload합니다. network/5xx
  실패 시 전환을 중단하고 token·선택 상태를 유지하며 사용자가 게임으로 돌아가 runtime을
  재개하거나 다시 시도할 수 있습니다.
- 저장이나 세션 확인이 `401/403`이면 현재 local과 `pending-unsynced` marker는 보존하고
  access token만 폐기해 로그인 화면으로 돌아갑니다. 재로그인 뒤 marker가 있으면 위
  선택 모달로 복구합니다. network/timeout/`5xx`는 token을 폐기하지 않고 retry 화면이나
  다음 직렬 저장 재시도를 사용합니다.
- `beforeunload`에서는 네트워크 완료를 믿지 않고 현재 캐릭터 로컬 저장만 수행합니다.

## 오류·로그·관리자 응답의 비밀정보 경계

- 인증 경로의 FastAPI `422`는 오류의 `loc`·`type`·`msg`를 유지하되 비밀번호,
  비밀번호 확인과 전체 인증 body의 `input`을 응답에서 제거합니다.
- SQLAlchemy engine은 application `DEBUG`와 관계없이 항상 `echo=False`,
  `hide_parameters=True`입니다. 비밀번호 해시와 raw snapshot이 SQL bind parameter나
  오류 로그에 노출되지 않도록 합니다.
- 관리자 save summary는 `saveVersion`, `gold`, `level`, `currentCharacterId`,
  `currentZoneIndex`, `currentZoneType`, 네 item count와 `createdAt`의 명시 allow-list만
  반환합니다. 문자열은 160자로 제한하고 scalar가 아닌 값, 임의 `summary_json` 키와
  전체 `snapshot_json`은 반환하지 않습니다.

## 화면 원칙

- 게임 배경을 어둡게 가린 전체 화면 로그인/회원가입 gate를 먼저 표시합니다.
- 슬롯 화면은 8칸을 항상 보여주며 데스크톱 2열, 좁은 화면 1열입니다.
- 빈 슬롯 생성과 캐릭터 삭제는 브라우저 기본 `alert`/`confirm`을 쓰지
  않고 게임 스타일의 확인·취소 modal로 처리합니다.
- 삭제 전에는 대상 캐릭터, 없어지는 진행 데이터와 확인 문구를 명확히 보여줍니다.
- 사용자 입력과 서버 응답은 `innerHTML`로 직접 삽입하지 않고 text node 또는 escape
  처리를 사용합니다.
- focus 이동, `Escape`, label, 상태 알림, 좁은 화면 버튼 배치를 함께 검증합니다.
- 관리자 페이지는 로그인 및 관리자 권한을 확인하기 전 기존 관리 API와 회원 정보를
  요청하지 않습니다.

## 공개 배포 전 남은 보안 보강

v370은 로컬 구현·검증 단계이며 Render backend와 Static Site에는 배포하지 않습니다.
현재 공개본은 계속 v351입니다. 공개 회원가입을 열기 전 다음 항목을 별도 단계에서
결정하고 검증해야 합니다.

1. 로그인·회원가입 IP/계정별 rate limit과 반복 실패 지연
2. 비밀번호 변경·분실 복구와 관리자 안전 복구 절차
3. 서버측 session/refresh token 또는 현재 단기 access token 정책의 최종 선택
4. ASGI 계층의 HTTP raw request body 크기 사전 제한
5. HTTPS 전용 동작, CSP와 XSS 회귀, token 저장 방식 재검토
6. 이용약관·개인정보 고지와 계정/데이터 삭제 정책
7. 소셜 로그인 도입 시 provider-neutral 연결 테이블과 계정 연결/해제 정책
8. 다중 기기 동시 접속의 save revision, 충돌 해결과 낙관적 잠금 정책
9. v370 backend image와 legacy static을 같은 승인 단위로 게시·배포하는 exact-SHA gate

새 secret, extension, 별도 외부 서비스와 DB migration은 이번 로컬 구현에 필요하지
않습니다. 실제 최초 관리자 지정은 기호가 자신의 계정을 직접 만든 뒤 별도 로컬 확인
단계에서 수행합니다. 비밀번호나 dev key 값은 채팅에 보내지 않습니다.

## 검증 상태 — 완료

v370 focused/browser/core 최종 검증을 모두 통과했습니다.

- backend account auth focused smoke: PASS
- backend account-admin focused smoke: PASS
- frontend account gate와 admin account management smoke: PASS
- v369 아이콘 회귀 smoke: PASS
- Python compileall: PASS
- 관련 JavaScript `node --check`: PASS
- runtime blocking-I/O strict 검사: PASS
- backend route map: 40 operations / PASS
- legacy static build와 static smoke: PASS
- GitHub/GHCR reproducibility hash 5개 동기화와 strict/fail-closed smoke: PASS
- `bash tools/run_smoke_core.sh`: backend `.venv` 활성화, 자식 프로세스
  `DEBUG=false` 조건에서 최종 PASS
- 실제 브라우저 desktop/mobile 로그인·회원가입 화면과 `pending-unsynced` 선택 모달:
  QA PASS, overflow 0, console error 0
- 최종 reviewer가 확인한 즉시 수정 blocker: 없음

이번 구현 준비 과정에서는 실제 local/Neon DB write, seed, restore, Alembic mutation,
Render/GHCR 배포를 실행하지 않았습니다. 새 secret, extension, 권한과 설치도 필요하지
않았습니다. 개발 서버 재시작도 필요하지 않았습니다.
