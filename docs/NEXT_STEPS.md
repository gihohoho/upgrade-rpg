# Next Steps — v312

1. `python tools/check_production_managed_postgres_reverse_proxy_selection.py --strict`
2. `python tools/render_production_compose_config.py --execute --confirm-stage v312-config-render-only`
3. config render 결과를 전달
4. backend image registry/source/digest 승인 형식 검토
5. pull/build는 각각 별도 승인
6. 관리형 PostgreSQL provider와 reverse proxy 제품은 실제 배포 환경에 맞춰 선택

실제 secret, DB 연결, container/network/volume 변경은 아직 실행하지 않습니다.
