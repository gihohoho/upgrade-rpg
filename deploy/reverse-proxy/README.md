# External reverse proxy HTTPS boundary — v312

운영 공개 진입점은 **외부 reverse proxy의 HTTPS 443**으로 확정했습니다. 제품은 아직 고정하지 않습니다. 관리형 ingress, Caddy, Nginx 등 실제 운영 위치가 결정되기 전 특정 제품 설정을 넣으면 DNS·인증서·네트워크 책임이 성급히 고정될 수 있기 때문입니다.

현재 고정된 계약:

- 외부 사용자는 HTTPS `443`으로만 접근
- HTTP `80`을 사용할 경우 HTTPS redirect 전용
- FastAPI `8000`은 host에 publish하지 않음
- proxy와 backend는 사전에 생성된 `EDGE_NETWORK_NAME` network로 연결
- proxy upstream은 `http://backend:8000`
- `/api/v1/health`를 proxy 외부 공개 health endpoint로 사용하지 않을 수 있음
- forwarded headers는 신뢰 proxy 범위를 확정한 뒤에만 활성화
- 실제 DNS, certificate/key, ACME 계정, proxy image는 아직 미선택·미적용

다음 제품 선택 시 확인할 항목:

1. DNS와 certificate 발급/갱신 책임
2. WebSocket 및 긴 요청 timeout 필요 여부
3. body size, rate limit, security header 정책
4. 실제 client IP 전달과 trusted proxy 범위
5. access/error log 보관 및 개인정보 최소화
6. backend healthcheck와 무중단 교체 방식

실제 reverse proxy container 또는 host 설정은 별도 승인 전 생성하거나 실행하지 않습니다.
