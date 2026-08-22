# Upgrade RPG Codex handoff — v377

새 채팅은 루트 [AGENTS.md](AGENTS.md)를 먼저 읽고 이 문서를 이어서 사용합니다. 더 자세한 현재 상태는 [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)가 기준입니다.

```txt
latest: v377.public-email-delivery-repaired
strict result: public-email-delivery-repaired
next safe stage: confirm-test-mail-arrival-and-continue-remaining-account-gates
source head: v377_auth_email_public_security
local/Neon DB current: v377_auth_email_public_security / v377_auth_email_public_security
v377 apply/stamp/downgrade: local 1/0/0; Neon 1/0/0
email rollout approval/execution: yes/public-live
public backend/static: v377 Live
```

## 이번 체크포인트

- v371 이메일 인증·복구·삭제와 v377 rate limit, JSON 파싱 전 body cap, semantic outbox, 미인증 identity 회수, 202·429·413 frontend 계약이 공개 서비스에 배포됐습니다.
- private environment와 ACL 준비, `email-validator==2.3.0`·`dnspython==2.8.0` Linux runtime/musllinux/dev lock, local Brevo 실제 Naver 메일→링크 인증→로그인→캐릭터 슬롯 8개 E2E는 완료 증거로 보존합니다.
- stale `8db9bcb`와 `recovery1` marker/evidence는 삭제·덮어쓰기하지 않았습니다. 최종 `recovery2` synthetic fixture의 `v295 → v377 → v295 → v377`을 1회 통과한 뒤 untouched Neon의 fresh custom backup과 v295→v377 apply를 각각 1회 완료했습니다.
- Neon apply는 기존 22개 table을 `SHARE ROW EXCLUSIVE`로 잠근 단일 transaction에서 수행했습니다. legacy 748 rows 변화 0, 25개 model table parity, 최종 revision `v377_auth_email_public_security`을 확인했습니다.
- DB reset·seed·restore·stamp·actual downgrade와 자동 retry는 실행하지 않았습니다. 운영 rollback은 additive v377 DB를 유지하고 이전 image로만 수행합니다.
- GitHub Actions run `32576889295`의 `run_attempt=1`이 linux/amd64 image를 게시·서명·검증했습니다. production image는 `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:a91d020c6b8abfbbcca56c1ff3ff7736c155fd43d854398e42bb0e42450ec994`입니다.
- Render 기존 backend service에는 email/security 환경변수 35개를 값 노출 없이 저장했습니다. backend deploy `dep-da4qqi3tqb8s738l68h0`은 새 exact digest로 live이며 자동 retry는 없었습니다.
- legacy static deploy `dep-da4qr867bikc73aekck0`은 commit `ceea14c20ac8604d453930d8f6c5127f00236352`에서 1회 build되어 live입니다.
- 공개 backend health는 HTTP 200입니다. auth malformed/schema 요청은 422와 `Cache-Control: no-store`, 허용된 Naver 테스트 주소의 인증메일 재요청은 generic 202 accepted와 `no-store`를 반환해 이전 `auth_protection_unavailable`·이메일 보안 미준비 503이 사라졌습니다.
- 첫 production 메일 미도착의 원인은 Brevo가 Render shared outbound IP를 차단한 것이었습니다. Render가 표시한 공식 CIDR `74.220.52.0/24`, `74.220.60.0/24`를 Brevo Authorized IP에 등록한 뒤 인증 메일이 provider에서 Delivered로 확인됐습니다.
- 그 메일은 실제 전송됐지만 outbox 성공 마감 중 `completed_at`보다 먼저 `sent` 상태가 autoflush되어 CHECK 제약에 걸렸습니다. `de3ae5d`에서 성공 상태 필드 설정 순서를 고쳤고 회귀 검사를 추가했습니다.
- 승인된 preparation `cd357de032425138d44323dd3060bbbf5b6a45d8`에서 authorization `46c9e7e33d866b160b6f4a8f36d5b68dabe3ece4`, immediate closure `e07474d5b5411dd805736687d1003f451298dae4`, evidence record `3e3516299a72e47c6d85597f8c0b60db5cb11a46`를 push했습니다. GitHub Actions run `32587614153`의 최초 1회가 signed digest `sha256:80e8f57618b2bd8bbac37fd63381e454434e06b67eff0cd8f4327796bdc1c677`를 게시했고 Render backend deploy `dep-da4tp7nqj5pc73b6l910`이 live입니다.
- 배포 뒤 공개 비밀번호 재설정 요청은 202와 `no-store`였고, Neon의 최신 outbox와 token은 1회 시도로 `sent`, provider 기록 존재, 오류 없음으로 마감됐습니다. 이미 인증된 테스트 계정의 인증메일 재전송은 의도대로 suppressed됐습니다.
- 공개 index는 로그인·회원가입·아이디 찾기·비밀번호 재설정·인증메일 재요청 UI를 표시하고, admin은 미로그인 상태에서 관리자 계정 확인 gate를 표시합니다.
- owner bootstrap은 별도 one-shot이며 실행하지 않았습니다.

## 바로 할 일

1. Naver 테스트 메일함에서 2026-08-23 02:32 KST 무렵 요청한 비밀번호 재설정 메일의 실제 도착 여부만 확인합니다. 서버·provider 접수와 outbox/token `sent`는 이미 확인했으므로 같은 요청을 반복하지 않습니다.
2. 공개 회원가입 확대 전에 server session/refresh/revoke, save revision/CAS, CSP/XSS·브라우저 token 저장 정책, 개인정보 보관·삭제·문의·복구 정책을 차례로 완료합니다.

## 안전 경계

- 실제 secret·token·password·DB URL·메일 본문은 출력·문서·Git artifact에 남기지 않습니다.
- 완료된 migration, GitHub Actions, Render backend/static deploy를 단순 확인 목적으로 다시 실행하지 않습니다.
- owner bootstrap, DB reset·seed·restore·stamp·actual downgrade, production 자동 retry는 별도 승인 없이는 실행하지 않습니다.
- 기호가 승인한 이메일 인증 rollout은 완료됐지만 남은 공개 계정 gate를 우회하는 승인은 아닙니다.

## 문서 기준

- 현재 판단: `docs/current/`
- 장기 기술 자료: `docs/reference/`
- 자동 생성 보고서: `docs/generated/`
- API 계약: `docs/contracts/`
- 실행 안내: `docs/guides/`
- 완료 이력: `docs/archive/history/`

문서 체계는 [Documentation System](docs/DOCUMENTATION_SYSTEM.md), 전체 색인은 [Docs Hub](docs/README.md)가 기준입니다.
