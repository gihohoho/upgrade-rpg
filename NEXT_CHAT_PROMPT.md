기호의 게임 프로젝트 이전 채팅에서 이어서 진행합니다.

현재 안정 버전은 `v250.backend-admin-rollback-snapshot`이며 backend splitStatus는 `admin-schema-field-constraint-contract-v238`입니다. 기준 ZIP은 `rpg_v246_backend_admin_write_replay_safety_contract.zip`입니다.

현재까지 관리자 request payload/422, malformed JSON, Content-Type/Accept, media/size, header encoding, transport header 관찰, preview replay parsing, apply write guard 계약이 완료되었습니다.

특히 반드시 지킬 사항:
- FastAPI/Starlette/Pydantic 환경 차이는 먼저 실제 결과를 수집한 뒤 계약화합니다.
- 새 backend 계약 파일/routeContract/readiness를 추가할 때 frontend와 동시에 갱신하고 `smoke_backend_admin_frontend_contract_parity.py`를 반드시 통과시킵니다.
- 실제 DB 쓰기, env, seed, 인증, API 주소, 응답 body는 명시적 필요가 없으면 변경하지 않습니다.
- `Idempotency-Key`는 현재 미지원이며, 지원한다고 가정하지 않습니다.

다음 추천 작업은 `v247 backend admin preview side-effect static contract`입니다. preview service 메서드가 commit/flush/add/delete를 호출하지 않는지 정적으로 검증하고, apply 메서드만 mutation boundary인지 확인하세요. 실제 DB 쓰기는 하지 마세요.

터미널 명령 위에는 반드시 실행 위치를 한국어로 적고, git 명령은 한 블록으로 묶어주세요.
