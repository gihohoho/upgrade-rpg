# FastAPI 백엔드 구조 초안

## 목표

현재 브라우저 JS 안에 있는 저장/전투/드랍/강화 판정을 단계적으로 FastAPI로 옮깁니다.

## 폴더 구조

```txt
backend/
  app/
    main.py                FastAPI 앱 생성
    api/                   라우터 모음
    core/                  설정, 응답, 인증 공통
    db/                    DB 세션, Base
    models/                SQLAlchemy 모델
    schemas/               Pydantic 요청/응답 스키마
    services/              게임/관리자 비즈니스 로직
  alembic/                 DB 마이그레이션
  sql/                     설계 초안 SQL
```

## 서버 역할

```txt
프론트는 버튼 입력과 화면 표시 담당
FastAPI는 실제 판정 담당
PostgreSQL은 유저 데이터와 마스터 데이터 저장 담당
관리자 페이지는 마스터 데이터를 수정하는 운영 도구
```

## API 응답 표준

`docs/API_RESPONSE_CONTRACT.md`와 `src/api/api-response-contract.js`를 기준으로 합니다.

공통 형태:

```json
{
  "ok": true,
  "responseVersion": "game-api-response.v1",
  "type": "combat.attack",
  "data": {},
  "logs": [],
  "effects": [],
  "ui": {},
  "statePatch": {},
  "error": null
}
```

## 단계별 이전 계획

```txt
1. backend/ 뼈대 생성
2. PostgreSQL schema 초안 확정
3. JS 마스터 데이터를 JSON seed로 추출
4. /game/master-data 구현
5. /game/load, /game/save 구현
6. 장착/해제/강화 API 이전
7. 보스 소환/전투/드랍 API 이전
8. 관리자 API 제작
9. Vue 관리자 페이지 제작
```
