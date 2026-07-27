# Master-data latency focused fix와 blocking-I/O 감사 — v351

## 결론

전체 코드를 확인한 결과, 함수를 무조건 `async`로 바꿀 필요는 없습니다. 현재 backend의 FastAPI route는 모두 비동기이며, 비동기 함수 안에서 `requests`, `time.sleep`, 동기 파일 읽기, 동기 subprocess처럼 서버 전체를 멈추게 할 수 있는 호출도 발견되지 않았습니다.

이번 지연의 직접 원인은 공개 `/game/master-data` 응답이 약 1.83~1.98초 걸리는 반면 브라우저 제한이 1.5초였던 것입니다. 따라서 v351은 다음 두 가지에 집중합니다.

- 브라우저 master-data 기본 timeout: 1,500ms → 5,000ms
- backend 1KB 이상 응답: Starlette `GZipMiddleware`로 압축, `compresslevel=5`

v355에서 새 backend exact image와 v351 Static Site source를 Render에 각각 한 번 배포했고, 공개 master-data가 1,346ms·gzip·no-fallback으로 적용되는 것을 검증했습니다.

## 왜 모든 sync 함수를 async로 바꾸지 않았나

`sync 함수`라는 말 자체가 느리거나 나쁘다는 뜻은 아닙니다. 숫자 계산, 값 변환, 검증, 응답 조립처럼 기다릴 외부 작업이 없는 함수는 sync가 더 단순하고 적합합니다. 이런 함수를 `async`로 바꿔도 빨라지지 않고 `await`만 늘어납니다.

비동기가 중요한 곳은 네트워크, DB, 디스크처럼 결과를 기다리는 동안 다른 요청을 처리할 수 있는 I/O 경계입니다. 감사 결과는 다음과 같습니다.

| 검사 | 결과 |
|---|---:|
| backend runtime Python 파일 | 77 |
| async 함수 | 99 |
| sync 함수 | 200 |
| async FastAPI route | 28 |
| sync FastAPI route | 0 |
| async 내부 blocking-I/O 호출 | 0 |
| 예상하지 못한 async-without-await | 0 |
| frontend runtime 파일 | 70 |
| 동기 XHR·Atomics.wait 등 blocking 호출 | 0 |

`tools/**`, `backend/scripts/**`도 별도로 모두 스캔했습니다. Python 148개 파일에서 동기 호출 371개, JavaScript 94개 파일에서 동기 호출 126개가 집계됐습니다. 이 영역의 파일 작업과 subprocess는 서버 요청 중 실행되는 코드가 아니라 개발자가 한 번 실행하고 종료하는 CLI이므로 런타임 fail-closed 결함과 분리해 `intentional-one-shot-cli`로 분류했습니다.

## master-data DB 조회를 병렬화하지 않은 이유

`GameService.get_master_data()`는 이미 `async`이며 11개의 조회를 순차적으로 `await`합니다. 이 조회들은 하나의 SQLAlchemy `AsyncSession`을 공유합니다. 같은 session을 여러 task가 동시에 사용하도록 `asyncio.gather()`를 적용하면 session 상태 충돌이나 예측하기 어려운 DB 오류가 생길 수 있습니다.

따라서 v351에서는 위험한 병렬화를 하지 않았습니다. 후속 최적화가 필요하면 다음 중 하나를 별도 측정·검토해야 합니다.

1. master-data snapshot cache와 안전한 무효화 정책
2. 쿼리 수나 중복 데이터 감소
3. 독립 session을 사용하는 제한적 병렬 조회

현재 개인 프로젝트와 Render Free/Neon Free 구성에서는 timeout 여유와 전송 압축이 가장 작고 안전한 수정입니다.

## fail-closed 검사

`tools/check_runtime_blocking_io.py --strict`는 다음 문제를 발견하면 실패합니다.

- sync FastAPI route
- async backend 함수 안의 대표적인 동기 HTTP·sleep·subprocess·파일 I/O
- 승인되지 않은 async-without-await 함수
- frontend의 synchronous XHR, `Atomics.wait`, 동기 child process

현재 async-without-await 5개는 FastAPI dependency/health 또는 기존 async facade 계약을 유지하기 위한 짧은 함수로 명시적 allowlist에 있습니다. 새 항목이 생기거나 기존 항목이 사라지면 allowlist 재검토 없이 검사가 통과하지 않습니다.

sanitized evidence는 `deploy/review/master-data-latency-blocking-io-audit-v351.json`입니다.

## 배포와 콘텐츠 경계

v351을 공개 환경에 적용하려면 backend 새 GHCR image 게시·isolated validation·Render exact-image deploy와 frontend Static Site deploy가 필요합니다. 모두 clean pushed exact SHA를 기준으로 별도 승인 범위를 준비하며 자동 deploy·retry는 하지 않습니다.

콘텐츠 추가·수정 시작 시점은 아직 아닙니다. 다음 두 조건을 실제 공개 환경에서 확인한 뒤 기호에게 먼저 알립니다.

- 공개 게임이 backend master-data를 fallback 없이 로드
- 관리자 guarded 콘텐츠 작업 흐름 검증 완료
