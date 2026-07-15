# Next Steps — v313

1. `python tools/check_backend_image_source_digest_policy.py --strict`
2. registry provider 선택
3. namespace/repository 선택
4. target platform 선택
5. base image exact digest 검토
6. pull/build/push는 각각 별도 승인
7. 이후 관리형 PostgreSQL provider와 reverse proxy 제품 선택

실제 secret, registry credential, image/container/network/volume, DB에는 아직 변경하지 않습니다.
