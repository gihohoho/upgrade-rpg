# Next Steps — v334

현재 production image와 isolated runtime 검증은 완료됐고 운영 배포 계획도 검토했습니다. 다음에는 실제 운영 공급자·host·DB·proxy·domain·secret 주입 위치를 확정합니다.

모든 입력이 준비되기 전에는 deploy 승인을 열지 않습니다. 입력을 반영한 실행 준비 commit을 만든 뒤 기호가 정확한 40자리 SHA를 별도 승인하면, 그 문서에 적힌 범위에서만 실제 deploy합니다.

세부 목록은 `PRODUCTION_DEPLOYMENT_PLAN.md`, 전체 순서는 `ROADMAP.md`를 봅니다.
