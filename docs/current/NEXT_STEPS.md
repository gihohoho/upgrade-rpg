# Next Steps — v357

## 현재 위치

- Render backend와 Static Site는 v351 공개 버전으로 Live입니다.
- Neon PostgreSQL 16 초기화와 exact v295 상태는 완료됐습니다.
- 12단계 `607%`에 이어 16단계 `무의식 : 넥스의 몽환의 어둠 +20 = 2121%` 실측 기준을 반영했습니다.
- 12→16단계 +20 목표는 단계당 `1.36721871444...`배 기하 보간하고 17단계 이후 같은 비율로 추정 외삽합니다.
- 14/15/17/18단계 +20 스킬 피해는 `1134.7 / 1551.3 / 2899.9 / 3964.8%`입니다.
- 16단계 +1~+19와 12~39단계 전 강화 레벨의 새 스킬 피해 공식을 검증했습니다.
- 17단계 `2097179 / 803447%`, 18단계 `851B / 7506%` 비대상 기준도 변경 없이 고정했습니다.
- 별도 공식 감사에서 추가 스킬 계수의 기존 외삽이 22단계부터 감소하고 33단계부터 음수가 되는 문제를 발견했으며, 이번 스킬 피해 전용 범위에서는 변경하지 않았습니다.
- generated seed, Neon DB, backend image는 변경하지 않았습니다.
- v357 static-only 배포 gate는 아직 준비되지 않았고, 공개 배포도 승인·실행되지 않았습니다.
- v357 정적 소스는 아직 공개 Static Site에 배포하지 않았습니다.

## 바로 다음 순서

1. 기존 Static Site ID, exact source commit, auto-deploy Off, 수동 deploy 1회와 금지 범위를 고정하는 v357 static-only fail-closed 계약/checker를 별도 준비합니다.
2. 기호가 그 gate 준비 commit의 정확한 40자리 SHA를 별도 승인할지 결정합니다.
3. 승인되면 기존 Render Static Site를 계약에 고정한 exact commit으로 수동 배포 한 번 실행합니다.
4. 공개 게임에서 12단계 `607%`, 16단계 `2121%`, 14·15·17단계 이후 증가값과 backend master-data 무폴백 상태를 read-only로 확인합니다.
5. sanitized 배포 증거와 handoff를 갱신합니다.
6. 이후 기호가 선택하는 다음 콘텐츠·밸런스 범위를 별도 작업으로 진행합니다.

## 이번 다음 단계에 포함되지 않는 것

- backend image build/push/deploy
- Neon DB write, seed import, schema 변경, Alembic mutation
- Render env·secret 변경
- 관리자 write 기능 실행
- 자동 deploy, 자동 retry, custom domain/DNS
- 이번 요청 밖의 장비·게임 밸런스 변경

공식과 감사 세부 내용은 `EQUIPMENT_PROGRESSION_FORMULA_AUDIT.md`를 봅니다.
