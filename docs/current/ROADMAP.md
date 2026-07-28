# Roadmap — v357

## 현재 체크포인트

```txt
Neon PostgreSQL 16 initialization: complete
Render backend v351: Live
Render Static Site v351: Live
public master-data no-fallback: verified
first content change: refined with tier 16 anchor and verified
v357 static-only deployment gate: not prepared
v357 static deployment: not approved / not executed
next safe stage: prepare-v357-static-content-deploy-exact-sha-gate
```

## 진행 순서

1. v357 static-only fail-closed 배포 계약/checker를 별도 준비합니다.
2. gate 준비 commit의 exact SHA 승인 전에는 공개 배포를 실행하지 않습니다.
3. 승인되면 기존 Static Site에만 exact source 수동 deploy 1회를 실행합니다.
4. 공개 게임에서 장비 수치와 무폴백 master-data를 read-only로 검증합니다.
5. 결과를 sanitized evidence와 handoff에 기록합니다.
6. 다음 콘텐츠·밸런스 요청을 별도 범위로 구현합니다.
7. custom domain/DNS와 SLA production 전환은 계속 보류합니다.

코드 또는 backend dependency가 바뀌는 후속 작업은 새 image 공급망 절차를 다시 적용합니다. 이번 v357 변경은 legacy Static Site JavaScript 계산식만 바뀌므로 backend image와 DB 작업이 필요하지 않습니다.
