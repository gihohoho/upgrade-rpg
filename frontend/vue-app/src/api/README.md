# Vue API Layer — v277 + v382 admin Preview

이 폴더는 Vue 앱의 FastAPI 조회와 side-effect 없는 Preview client 공간입니다.

원칙:

- 일반 조회는 `GET`만 사용
- 관리자 Preview 5개만 `POST`와 `dryRun: true` 사용
- Apply/`PUT`/`PATCH`/write `DELETE` 미연결
- 공개 GET 인증 interceptor 미구현
- 관리자 GET은 typed admin store가 Bearer와 `no-store`를 전달
- `.env` 변경 없음

## 현재 실제 화면 연결

- `GET /api/v1/health`
- `GET /api/v1/admin/requirements`
- `GET /api/v1/admin/master-data/domains`
- `GET /api/v1/admin/master-data/catalog`
- `GET /api/v1/admin/master-data/detail`
- `GET /api/v1/admin/master-data/relations`
- `GET /api/v1/admin/master-data/create-blueprint`
- `GET /api/v1/admin/change-logs`, `/change-logs/{id}`
- `POST /api/v1/admin/master-data/create-preview`, `/edit-preview`
- `POST /api/v1/admin/change-logs/{id}/rollback-preview`, `/create-delete-preview`, `/create-delete-restore-preview`

`adminPreviewApi.ts`만 Preview POST를 소유합니다. 이 모듈에는 Apply route, 확인 문구, `X-Admin-Dev-Key`가 없습니다.

도메인 응답:

```txt
response.payload.domains
```

카탈로그 응답:

```txt
response.payload.columns
response.payload.rows
```

카탈로그 고정 조회:

```txt
limit=20
page=1
sort=id_asc
```

상세/관계 wrapper는 `rowId`를 받아 실제 backend query `id`로 변환합니다.

## 설치/실행

새 라이브러리는 없습니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
npm run dev
```
