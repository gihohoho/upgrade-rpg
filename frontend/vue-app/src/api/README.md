# Vue API Layer — v277

이 폴더는 Vue 앱의 FastAPI read-only client 공간입니다.

원칙:

- `GET`만 사용
- `POST`, `PUT`, `PATCH`, `DELETE` 미사용
- Preview/Apply/write 미연결
- 인증 interceptor 미구현
- `.env` 변경 없음

## 현재 실제 화면 연결

- `GET /api/v1/health`
- `GET /api/v1/admin/requirements`
- `GET /api/v1/admin/master-data/domains`
- `GET /api/v1/admin/master-data/catalog`

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
