# FastAPI 백엔드 구조 — v370

## 목표

현재 브라우저 JS 안에 있는 저장/전투/드랍/강화 판정을 단계적으로 FastAPI로 옮깁니다.
v370에서는 그 기반 위에 회원가입·로그인, 계정별 캐릭터 슬롯 8개, 캐릭터별 save
snapshot과 관리자 회원 관리를 로컬 소스에 추가했습니다.

## 폴더 구조

```txt
backend/
  app/
    main.py                FastAPI 앱 생성
    api/                   라우터 모음
    core/                  설정, 응답, 인증 공통
    db/                    DB 세션, Base
    models/                SQLAlchemy 모델
    schemas/               Pydantic 요청/응답 스키마
    services/              게임/관리자 비즈니스 로직
  alembic/                 DB 마이그레이션
  sql/                     설계 초안 SQL
```

## 서버 역할

```txt
프론트는 버튼 입력과 화면 표시 담당
FastAPI는 실제 판정 담당
PostgreSQL은 유저 데이터와 마스터 데이터 저장 담당
관리자 페이지는 마스터 데이터를 수정하는 운영 도구
```

## v370 계정과 캐릭터 저장 구조

새 테이블이나 Alembic revision을 만들지 않고 기존 스키마를 사용합니다.

- `users`: 소문자 아이디, bcrypt 비밀번호 해시, 활성 상태, 관리자 여부
- `user_profiles`: 회원가입 때 함께 만드는 계정 프로필 1:1 행
- `user_save_snapshots`: `character-1`~`character-8` 고정 슬롯과 전체 save snapshot
- `admin_change_logs`: 최초 관리자 bootstrap과 회원 상태 변경 감사 기록
- `characters`: `weapon_master` 같은 선택 가능한 캐릭터 종류 마스터 데이터

`characters`와 브라우저 `player.userCharacters`는 계정 슬롯이 아닙니다. 캐릭터 한
명은 `user_save_snapshots` 한 행을 사용하고, `summary_json.accountCharacter`에 슬롯
번호·표시 이름·직업 코드·생성 시각과 별도 32자리 고유 ID를 보관합니다. 캐릭터를
삭제한 뒤 같은 슬롯을 다시 만들어도 고유 ID가 달라 오래된 로컬 캐시가 연결되지
않습니다.

저장·불러오기는 세 조건을 모두 확인합니다.

1. Bearer token에서 확인한 현재 계정 ID
2. `character-1`부터 `character-8`까지의 고정 슬롯 키
3. 현재 슬롯 metadata의 `accountCharacterId`

클라이언트가 보낸 `userId`로 소유자를 선택하지 않습니다. 저장 요청의 `snapshot`,
슬롯 키와 캐릭터 고유 ID를 안정적으로 직렬화한 크기는 2,000,000바이트 이하로
제한하지만, HTTP raw body를 JSON 파싱 전에 막는 ASGI 계층 cap은 공개 전 보강
항목입니다.

정상 load의 authoritative 원본은 서버 DB snapshot입니다. backend에 snapshot이 있으면
서버본을 사용하고 서로 다른 local은 활성값을 바꾸기 전에 복구 백업으로 보존합니다.
backend가 비어 있을 때만 계정·캐릭터가 일치하는 local을 초기 복구 원본으로 사용해
서버 저장 큐에 넣습니다. 저장 실패로 `pending-unsynced` marker가 있을 때는 프런트 모달이
local 재전송·서버본 사용·취소 중 하나를 명시적으로 선택하게 하며 자동 병합하지 않습니다.

자동·수동·캐릭터 전환·로그아웃 저장은 프런트의 단일 직렬 큐를 통과합니다. 전환은
runtime을 pause한 뒤 기존 큐와 마지막 snapshot write를 drain하고, 성공한 경우에만
선택 상태/token 정리와 reload를 실행합니다. 서버 revision과 낙관적 잠금이 아직 없으므로
다중 기기 동시 저장 충돌 해결은 공개 전 후속입니다.

## v370 인증 경계

- 비밀번호는 직접 dependency인 `bcrypt 5.0.0`으로 해시하고 CPU 작업은 worker
  thread에서 수행합니다.
- 기존 `JWT_SECRET_KEY`로 알고리즘이 고정된 HS256 24시간 access token을 서명합니다.
- 각 인증 요청에서 `users`를 다시 읽고 비활성 계정은 이미 발급된 token도 거절합니다.
- 회원가입은 항상 `is_admin=false`이며 비밀번호 원문·해시와 token을 로그나 관리자
  응답에 포함하지 않습니다.
- 최초 관리자는 로그인 가능한 관리자가 없을 때 로그인 계정과 별도
  `X-Admin-Dev-Key`를 함께 확인하는 1회 bootstrap으로만 지정합니다.
- 기존 콘텐츠 관리자 write는 실제 관리자 Bearer 권한을 기본으로 하고, 위험한 apply는
  기존 dev key를 두 번째 방어선으로 유지합니다.
- 인증 경로의 FastAPI `422` handler는 `loc`·`type`·`msg`를 유지하지만 비밀번호·확인
  필드와 인증 body의 `input`을 제거합니다.
- SQLAlchemy engine은 application debug와 무관하게 `echo=False`,
  `hide_parameters=True`를 고정해 password hash와 raw snapshot bind 값을 숨깁니다.
- 관리자 snapshot summary는 명시된 11개 진단 scalar allow-list와 문자열 160자 제한만
  허용하고 raw `snapshot_json`과 임의 `summary_json` 키는 반환하지 않습니다.

`401/403`에서는 브라우저 local과 미전송 marker를 보존한 채 token을 폐기하고 재로그인
복구 선택으로 돌아갑니다. network/timeout/`5xx`에서는 token과 선택 상태를 유지해 retry와
다음 직렬 저장을 허용합니다.

서버측 session/refresh token, 개별 기기 원격 로그아웃, 로그인 rate limit,
비밀번호 변경·복구는 아직 구현하지 않았으며 공개 전 보강 범위입니다.

## API 응답 표준

`docs/contracts/API_RESPONSE_CONTRACT.md`와 `src/api/api-response-contract.js`를 기준으로 합니다.

공통 형태:

```json
{
  "ok": true,
  "responseVersion": "game-api-response.v1",
  "type": "combat.attack",
  "data": {},
  "logs": [],
  "effects": [],
  "ui": {},
  "statePatch": {},
  "error": null
}
```

## 단계별 이전 현황

```txt
1. backend 뼈대·PostgreSQL schema·JSON seed·`/game/master-data`: 완료
2. 인증된 `/game/load`, `/game/save`, 계정 캐릭터 슬롯: v370 로컬 구현 준비
3. 회원가입·로그인과 관리자 회원 관리: v370 로컬 구현 준비
4. 장착/해제/강화 API 이전: 후속
5. 보스 소환/전투/드랍 API 이전: 후속
6. legacy 관리자 콘텐츠 API의 운영 인증·쓰기 절차: 추가 보강 후 공개
7. Vue 관리자 페이지 이전: 후속, 현재 실제 화면은 legacy `admin.html`
```

공개 Render backend는 계속 v351 exact image입니다. v370에서는 DB write·seed·migration,
새 secret, Render env 변경, image 게시와 deploy를 실행하지 않았습니다. v370
focused/browser/core, route map 40 operations, runtime blocking-I/O strict와 core smoke는
모두 통과했으며 상세 실제 결과는 `CURRENT_STATUS.md`에 기록합니다.
