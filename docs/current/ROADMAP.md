# Roadmap — v288

## 완료 흐름

- v268~v275 구조/route/read-only client 준비
- v276~v281 Vue 관리자 GET 이식
- v282~v284 PostgreSQL/Alembic readiness 및 async env 수정
- v285~v286 PostgreSQL runtime 비파괴 점검과 baseline 전략 초안
- v287 Windows UTF-8/cp949 subprocess 출력 수정 및 실제 DB 결과 반영
- v288 상세 PostgreSQL/SQLAlchemy schema 동등성 읽기 전용 preflight

## 현재 경계

현재 DB에는 22개 테이블과 748개 row가 있고 Alembic 이력은 없습니다.
기존 데이터 보존형 baseline 전략으로 확정됐지만, 아직 revision 생성이나 stamp는 실행하지 않습니다.

계속 보류:

- Preview/Apply/write 확대
- 관계 편집
- 인증
- DB schema/env/seed 변경
- migration 생성/적용/stamp
- Docker container/volume 변경 및 삭제
- 게임 콘텐츠

## 다음 작업 — v289

1. `check_postgres_schema_equivalence.py` 실제 결과 수집
2. 구조 차이 0개인지 확인
3. backup 파일 형식/위치/보존 규칙 문서화
4. 별도 임시 PostgreSQL DB 이름과 포트 결정
5. 아직 backup 실행, revision 생성, stamp는 사용자 승인 전 보류

## 이후 — 사용자 승인 후

- PostgreSQL backup 생성 및 restore 리허설
- Alembic versions/template 준비
- 최초 revision 생성 및 전체 검토
- 별도 빈 DB upgrade/downgrade 왕복
- 최초 revision 결과와 SQLAlchemy metadata 동등성 확인
- 기존 DB baseline stamp 여부 최종 승인
- 인증/관리자 권한 설계
- 관리자 Vue 이식 확대
- 게임 Vue 이식
- 배포 직전 안정화
