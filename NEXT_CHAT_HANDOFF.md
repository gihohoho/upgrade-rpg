# Upgrade RPG Codex handoff — v377

새 채팅은 루트 [AGENTS.md](AGENTS.md)를 먼저 읽고 이 문서를 이어서 사용합니다. 더 자세한 현재 상태는 [CURRENT_STATUS.md](docs/current/CURRENT_STATUS.md)가 기준입니다.

```txt
latest: v377.public-email-rollout-deployed
strict result: public-email-rollout-deployed
next safe stage: monitor-v377-public-email-delivery-and-remaining-account-gates
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
- 공개 index는 로그인·회원가입·아이디 찾기·비밀번호 재설정·인증메일 재요청 UI를 표시하고, admin은 미로그인 상태에서 관리자 계정 확인 gate를 표시합니다.
- owner bootstrap은 별도 one-shot이며 실행하지 않았습니다.

## 바로 할 일

1. Naver 테스트 메일함에서 이번 공개 재요청 메일의 실제 도착 여부를 확인합니다. generic 202는 계정 존재 여부를 숨기므로 메일 미도착만으로 provider 실패를 단정하지 않습니다.
2. 공개 로그와 outbox 상태를 값 노출 없이 관찰해 발송 행이 있으면 `sent` 또는 terminal 상태를 확인합니다. 같은 요청을 자동 재시도하지 않습니다.
3. 공개 회원가입 확대 전에 server session/refresh/revoke, save revision/CAS, CSP/XSS·브라우저 token 저장 정책, 개인정보 보관·삭제·문의·복구 정책을 차례로 완료합니다.

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
