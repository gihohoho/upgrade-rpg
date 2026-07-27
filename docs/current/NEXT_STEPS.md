# Next Steps — v356

## 현재 위치

- Render backend와 Static Site는 v351 공개 버전으로 Live입니다.
- Neon PostgreSQL 16 초기화와 exact v295 상태는 완료됐습니다.
- 첫 콘텐츠·밸런스 변경으로 12단계 이후 스킬 피해 공식을 수정했습니다.
- 12-1 `-초월- 어둠을 지배하는 고리 +20`은 `69.1B / 607% / 기존 모든 피해 173.9%`입니다.
- 1~12단계 일반 장비 60종과 12~39단계 새 스킬 피해 공식을 검증했습니다.
- generated seed, Neon DB, backend image는 변경하지 않았습니다.
- v356 static-only 배포 gate는 아직 준비되지 않았고, 공개 배포도 승인·실행되지 않았습니다.
- v356 정적 소스는 아직 공개 Static Site에 배포하지 않았습니다.

## 바로 다음 순서

1. v356 장비 공식 commit을 검증하고 `main`에 push합니다.
2. 기존 Static Site ID, exact source commit, auto-deploy Off, 수동 deploy 1회와 금지 범위를 고정하는 static-only fail-closed 계약/checker를 별도 준비합니다.
3. 기호가 그 gate 준비 commit의 정확한 40자리 SHA를 별도 승인할지 결정합니다.
4. 승인되면 기존 Render Static Site를 계약에 고정한 exact commit으로 수동 배포 한 번 실행합니다.
5. 공개 게임에서 12단계 `607%`, 13단계 이후 증가값, backend master-data 무폴백 상태를 read-only로 확인합니다.
6. sanitized 배포 증거와 handoff를 갱신합니다.
7. 이후 기호가 선택하는 다음 콘텐츠·밸런스 범위를 별도 작업으로 진행합니다.

## 이번 다음 단계에 포함되지 않는 것

- backend image build/push/deploy
- Neon DB write, seed import, schema 변경, Alembic mutation
- Render env·secret 변경
- 관리자 write 기능 실행
- 자동 deploy, 자동 retry, custom domain/DNS
- 이번 요청 밖의 장비·게임 밸런스 변경

공식과 감사 세부 내용은 `EQUIPMENT_PROGRESSION_FORMULA_AUDIT.md`를 봅니다.
