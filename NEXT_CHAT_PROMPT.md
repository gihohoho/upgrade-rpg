기호의 게임 프로젝트 이전 채팅에서 이어서 진행합니다.

현재 안정 버전은 `v241.backend-admin-validation-error-compatibility-contract`이며 backend splitStatus는 `admin-schema-field-constraint-contract-v238`입니다.

v240에서 관리자 요청 body 모델 10개의 정상 alias 직렬화(`dryRun`, `confirmText`, `baseValues`)와 대표 잘못된 payload의 FastAPI 422 `detail[].type/loc/msg` 계약을 추가했습니다. 검증은 격리된 FastAPI parsing app에서 수행되어 service 호출과 DB 쓰기가 없습니다. route path, API response body, DB, env, seed, auth, apply write guard는 변경하지 않았습니다.

다음 추천 작업은 `v241 backend admin validation error compatibility contract`입니다. malformed JSON 및 wrong content-type까지 request parsing 경계에서 검증하되 DB/service에는 접근하지 말고, FastAPI/Pydantic 버전별로 불안정한 input/context 값은 계약에서 제외해주세요.
