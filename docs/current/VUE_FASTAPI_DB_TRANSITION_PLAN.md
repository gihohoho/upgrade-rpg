# Vue/FastAPI/DB 전환 준비 계획

## 목적

지금까지 만든 HTML/JS 기반 게임과 관리자 도구를 바로 갈아엎지 않고, 검증된 기능과 계약을 보존한 상태에서 Vue + FastAPI + PostgreSQL 구조로 옮길 준비를 합니다.

## 원칙

1. 먼저 분석하고 문서화합니다.
2. 실제 파일 이동은 smoke 영향 범위를 확인한 뒤 진행합니다.
3. 기존 route path와 API response body는 유지합니다.
4. 기존 관리자 Preview/Apply 안전장치는 유지합니다.
5. 게임 콘텐츠 신규 개발은 전환 구조가 안정화된 뒤 진행합니다.

## 현재 legacy 후보

- `index.html`
- `admin.html`
- `src/api/admin/*.js`
- `src/ui`, `src/systems`, `src/state`, `src/rules`, `src/data`

이 파일들은 당장 제거하지 않습니다. Vue 전환 전까지는 기준 동작과 smoke 검증 대상입니다.

## Vue 전환 후보 구조

```text
frontend/
  legacy/
    index.html
    admin.html
    src/
  vue-app/
    src/
      app/
      pages/
      components/
      api/
      stores/
      router/
      styles/
```

실제 이동 여부와 시점은 다음 단계에서 smoke 경로 의존성을 확인한 뒤 결정합니다.

## Backend 정리 후보 구조

```text
backend/
  app/
    main.py
    core/
    api/
      v1/
        admin/
        game/
        auth/
    models/
    schemas/
    services/
    repositories/
    contracts/
  tests/
  tools/
```

현재 backend 구조를 먼저 분석하고, route 호환성 유지 계획을 세운 뒤 이동합니다.

## DB/Alembic 준비

- migration은 구조 변경용
- seed는 초기/테스트 데이터용
- 운영 데이터 변경은 관리자 Preview/Apply 흐름으로 처리
- rollback snapshot 정책은 DB 변경 전에 별도 검토

## 다음 채팅에서 먼저 할 일

- 현재 파일 구조를 실제로 출력해 분석
- smoke가 참조하는 경로 목록 확인
- legacy 이동 전 깨질 수 있는 곳 정리
- `PROJECT_STRUCTURE.md`를 최신 기준으로 갱신
