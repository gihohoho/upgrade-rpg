기호의 게임 프로젝트 이전 채팅에서 이어서 진행합니다.

현재 안정 버전은 `v245.backend-admin-transport-header-observation-contract`이며 backend splitStatus는 `admin-schema-field-constraint-contract-v238`입니다. 기준 ZIP은 `rpg_v245_backend_admin_transport_header_observation_contract.zip`입니다.

현재까지 request payload/422, malformed JSON, Content-Type/Accept negotiation, non-JSON media type, request-size ownership 계약이 완료되었습니다. 환경별 FastAPI/Starlette 차이가 있는 항목은 한 가지 결과로 단정하지 말고, 먼저 현재 환경에서 실제 결과를 수집한 뒤 허용 결과별 세부 `type/loc/msg`까지 검증하세요.

다음 추천 작업은 `v244 backend admin request header and encoding compatibility contract`입니다. UTF-8 한글 JSON, charset 파라미터 변형, 잘못된 byte encoding, 중복/이상 Content-Type 파라미터를 DB와 service 호출 없이 검증하세요. 실제 API 경로/응답 body/DB/env/seed/인증/write guard는 변경하지 마세요.

터미널 명령 위에는 반드시 실행 위치를 한국어로 적고, git 명령은 한 블록으로 묶어주세요.


다음 추천 작업은 `v245 backend admin request duplicate-header and transfer-encoding observation contract`입니다. 환경별 ASGI 클라이언트 차이를 먼저 수집하고 실제 API 동작은 변경하지 않습니다.


## v245에서 추가된 사항

- `backend/app/api/routes/admin_request_transport_header_observation_contract.py`
- `tools/smoke_backend_admin_request_transport_header_observation_contract.py`
- 중복 Content-Type/Accept 및 Content-Length/Transfer-Encoding을 ASGI/TestClient 관찰 범위로만 계약화
- 실제 wire framing, request-smuggling 방어, Content-Length 차단은 proxy/ASGI server 책임으로 명시
- backend/frontend parity smoke가 전체 extractedFiles와 routeContract를 정확히 비교하므로 새 계약 추가 시 양쪽을 반드시 동시에 갱신
