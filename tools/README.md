# tools

현재 폴더는 백엔드 분리 준비 과정에서 코드/스타일 검증에 사용한 보조 스크립트를 넣는 공간입니다.

운영 코드에는 직접 포함되지 않습니다.


## 현재 주요 도구

```txt
check_backend_ready.py        로컬 백엔드/Docker/PostgreSQL 준비 상태 점검
extract_seed_data.js          현재 JS 마스터 데이터를 JSON seed로 추출
smoke_seed_extraction.js      생성된 seed JSON 기본 검증
smoke_action_results.js       Action Result 구조 검증
smoke_api_response_contract.js API 응답 계약 검증
smoke_backend_foundation.js   backend/ 뼈대 파일 존재 검증
```

## seed 추출

프로젝트 루트에서 실행합니다.

```bash
node tools/extract_seed_data.js
node tools/smoke_seed_extraction.js
```
