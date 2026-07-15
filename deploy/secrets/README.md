# Production secret files

실제 secret 파일은 이 폴더나 Git/전달 ZIP에 넣지 않습니다.

운영 배포 플랫폼에서 다음 파일을 별도로 준비하고 `deploy/production.env`의 절대 경로로 연결합니다.

- PostgreSQL password secret
- PostgreSQL 서버 인증서를 검증할 승인 CA PEM

금지 사항:

- secret 값 커밋
- 실제 인증서/키 전달 ZIP 포함
- 로컬 기본 비밀번호 재사용
- `sslmode=disable`, `allow`, `prefer`, 검증 없는 `require` 사용
