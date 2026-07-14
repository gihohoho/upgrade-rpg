# Roadmap — v289

## 완료 흐름

- v268~v275 구조/route/read-only client 준비
- v276~v281 Vue 관리자 GET 이식
- v282~v284 PostgreSQL/Alembic readiness 및 async env 수정
- v285~v286 PostgreSQL runtime 비파괴 점검과 baseline 전략
- v287 Windows subprocess 출력 수정 및 실제 DB 결과 반영
- v288 PostgreSQL/SQLAlchemy 상세 schema 비교 preflight
- v289 PostgreSQL FLOAT alias 정규화 및 다음 채팅 handoff 정리

## 현재 경계

현재 DB에는 22개 테이블과 748개 row가 있고 Alembic 이력은 없습니다.
기존 데이터 보존형 baseline 대상으로 확정됐지만 revision 생성, upgrade, stamp는 실행하지 않습니다.

## 다음 작업 — v290

1. v289 schema checker 실제 재실행 결과 확인
2. 원본 DB에 영향을 주지 않는 backup/restore 리허설 계획 확정
3. backup 파일 민감정보/보관/제외 규칙 확정
4. 별도 restore rehearsal DB와 별도 migration test DB 경계 확정
5. 사용자 승인 전에는 실제 backup/restore/DB 생성 미실행

## 이후 — 사용자 승인 후

- PostgreSQL backup 생성
- 별도 DB restore 리허설
- 테이블·row count 동등성 확인
- Alembic versions/template 준비
- 최초 revision 생성 및 전체 검토
- 별도 빈 DB upgrade/downgrade 왕복
- 기존 DB baseline stamp 여부 최종 승인
- 인증/관리자 권한 설계
- 관리자 Vue 이식 확대
- 게임 Vue 이식
- 배포 직전 안정화

## 계속 보류

- 게임 콘텐츠 추가/밸런스 조정
- 관리자 Preview/Apply/write Vue 확대
- 인증 구현
- 기존 DB schema/data/env/seed 변경
- Docker volume 삭제
