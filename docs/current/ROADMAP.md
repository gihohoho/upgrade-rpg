# Roadmap — v306

## 완료

- PostgreSQL schema equivalence differences=0
- verified backup과 isolated restore rehearsal
- 최초 revision `v295_initial_schema` 자동/수동 검토
- isolated migration DB upgrade → downgrade base → upgrade 왕복
- rehearsal/source baseline stamp 및 post-check
- source/rehearsal application 22 tables / 748 rows digest 보존
- v305 baseline completion state 실제 통과

## 현재

- classification: `alembic-managed-baseline-complete`
- source/rehearsal/migration 모두 `v295_initial_schema`
- 검토된 revision 파일 1개
- v306 next-revision read-only preflight 준비 완료
- revision/autogenerate/upgrade/downgrade 미승인

## 다음 안전 순서

1. 기호님 PC에서 v306 preflight 실행
2. single graph/model snapshot/canonical schema/sequence 확인
3. Alembic candidate operation 0개면 새 revision 생성 보류
4. 후보가 있으면 schema change intent review
5. autogenerate는 별도 승인 전 금지
6. 향후 revision은 isolated migration DB에서 검토·왕복
7. source 적용은 다시 별도 승인

## 계속 금지

- source/rehearsal stamp 재실행
- 새 revision/autogenerate
- source/rehearsal/migration upgrade/downgrade
- DB create/drop/restore
- `.env`, seed, 인증, API body/route/write 변경
- Docker volume 삭제
- 게임 콘텐츠/밸런스 변경
