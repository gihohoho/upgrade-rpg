# Next Steps — v311

1. `python tools/check_production_capacity_tls_network_plan.py --strict` 사용자 PC 결과 수집
2. 현재 1 replica/1 worker와 `max_connections=40` review 후보 확인
3. 실제 예상 트래픽과 향후 2 replica 필요 여부 검토
4. 관리형 PostgreSQL 또는 bundled PostgreSQL TLS 운영 방향 승인
5. reverse proxy 제품/DNS/HTTPS certificate 운영 방향 승인
6. image digest source와 승인 기록 형식 확정
7. 별도 승인 후 production Compose `config` render-only 검토
8. build/pull/up/down은 각각 다시 별도 승인

실제 secret, CA, production Compose, DB 설정 및 migration은 아직 실행하지 않습니다.
