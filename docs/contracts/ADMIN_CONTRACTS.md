# Admin contracts

관리자 계약의 기준 원본은 `backend/app/services/admin_service_split_contract.py`입니다.

`python tools/contracts/sync_admin_contract_registry.py`를 실행하면 프론트의 `extractedFiles`와 `routeContract`가 백엔드 기준으로 자동 동기화됩니다.

새 계약 추가 순서:
1. 백엔드 계약 파일 추가
2. 백엔드 split contract 등록
3. sync 스크립트 실행
4. parity/readiness/core smoke 실행
