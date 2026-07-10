기호의 게임 프로젝트 이전 채팅에서 이어서 진행합니다.

현재 안정 버전은 `v243.backend-admin-request-media-size-boundary-contract`이며 backend splitStatus는 `admin-schema-field-constraint-contract-v238`입니다. 기준 ZIP은 `rpg_v243_backend_admin_request_media_size_boundary_contract.zip`입니다.

현재까지 request payload/422, malformed JSON, Content-Type/Accept negotiation, non-JSON media type, request-size ownership 계약이 완료되었습니다. 환경별 FastAPI/Starlette 차이가 있는 항목은 한 가지 결과로 단정하지 말고, 먼저 현재 환경에서 실제 결과를 수집한 뒤 허용 결과별 세부 `type/loc/msg`까지 검증하세요.

다음 추천 작업은 `v244 backend admin request header and encoding compatibility contract`입니다. UTF-8 한글 JSON, charset 파라미터 변형, 잘못된 byte encoding, 중복/이상 Content-Type 파라미터를 DB와 service 호출 없이 검증하세요. 실제 API 경로/응답 body/DB/env/seed/인증/write guard는 변경하지 마세요.

터미널 명령 위에는 반드시 실행 위치를 한국어로 적고, git 명령은 한 블록으로 묶어주세요.
