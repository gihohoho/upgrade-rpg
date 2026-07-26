# Render Web Service 실행 결과 — v347

## 현재 결론

Render Free Web Service `upgrade-rpg-api`가 Singapore에서 Live입니다.

- 공개 주소: `https://upgrade-rpg-api.onrender.com`
- service ID: `srv-d9iro458nd3s73acgmsg`
- first deploy ID: `dep-d9iro4l8nd3s73acgnmg`
- image: 승인된 GHCR exact digest
- plan: Free / 1 instance / 고정 월 비용 $0
- evidence: `deploy/review/render-service-initial-deploy-v347.json`

## 실행된 범위

승인된 preparation SHA `81d1c4faa59194e8928d54fbecac28694ab139ab`를 clean pushed `main`과 대조한 뒤 아래 작업을 실행했습니다.

1. Existing Image Web Service 한 개 생성
2. 서비스 이름 `upgrade-rpg-api`, Singapore, Free 선택
3. 승인된 환경변수 14개 주입
4. exact image 최초 deploy 한 번
5. platform health path `/api/v1/health` 설정
6. Render 내부 health 200과 Live 상태 확인
7. 공개 `/api/v1/health` HTTP 200 `status=ok` 확인
8. `/api/v1/health/db`를 한 번 요청해 HTTP 200 `status=ok` 확인

`NEON_DIRECT_DATABASE_URL`과 `NEON_POOLED_DATABASE_URL`은 Render에 넣지 않았고 로컬 보관용으로만 유지합니다. 실제 `DATABASE_URL`, JWT/admin secret은 문서·Git·채팅·로그·evidence에 기록하지 않았습니다.

## 실제 runtime 관찰

앱/예시의 기본 포트 힌트는 `8000`이지만 Render가 Free Web Service runtime에 reserved `PORT=10000`을 주입했습니다. 이미지 CMD가 `PORT`를 따르므로 `10000`에서 정상 기동했고 Render health check도 성공했습니다. worker는 1개입니다.

Docker command override와 pre-deploy command는 비어 있습니다. image-backed service에는 auto deploy를 사용하지 않으며 persistent disk, custom domain, DNS, payment method도 추가하지 않았습니다.

## 실행하지 않은 것

- DB create/delete/restore/reset/seed/write
- Alembic revision/stamp/upgrade/downgrade
- image 변경 또는 tag 배포
- custom domain, DNS, 결제수단 변경
- automatic retry, 두 번째 deploy
- 인증/API write logic, Vue write, 게임 콘텐츠·밸런스 변경

첫 deploy approval은 소비됐고 재사용할 수 없습니다. `tools/prepare_render_local_environment.py --verify-execution-approval`도 완료 상태에서 재실행을 거부합니다.

## 다음 단계

현재 backend는 public HTTPS에서 동작하지만 `CORS_ORIGINS=[]`입니다. frontend 배포 위치를 먼저 정한 뒤 그 exact origin만 허용하는 CORS 변경과 frontend API base URL 배포 계획을 별도 검토합니다. 무료 instance는 idle 시 잠들어 첫 요청에 cold start가 발생할 수 있습니다.
