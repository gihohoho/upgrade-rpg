기호의 게임 프로젝트 이전 채팅에서 이어서 진행합니다.

현재 안정 버전은 `v242.backend-admin-request-content-negotiation-contract`이며 backend splitStatus는 `admin-schema-field-constraint-contract-v238`입니다.

v240에서 관리자 request body alias 직렬화와 대표 FastAPI 422 detail 계약을 추가했고, v241에서 malformed JSON·빈 body·잘못된 text/plain Content-Type 오류 호환성을 고정했습니다. v242에서는 `application/json; charset=utf-8`, Content-Type 없는 JSON(환경에 따라 정상 JSON 디코딩 200 또는 안정적인 model_attributes_type 422 허용), 최상위 배열/문자열, 빈 객체와 빈 body의 차이, Accept 헤더별 기본 JSON 응답을 격리된 FastAPI 앱에서 검증합니다. 모든 계약은 service 호출 0, DB 쓰기 0이며 route path, API response body, DB, env, seed, auth, apply write guard는 변경하지 않았습니다.

다음 추천 작업은 `v243 backend admin request size and media-type boundary contract`입니다. 바이너리/form 계열 미디어 타입과 요청 크기 경계를 실제 DB/service 호출 없이 검증하고, 기존 v242 readiness 및 프론트/백엔드 정적 계약 목록을 반드시 함께 갱신해주세요.
