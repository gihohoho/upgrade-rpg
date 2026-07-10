# Admin Page URL Helper

Version: `v113: admin page URL helper`

## 목적

`admin.html` 직접 접근 안내를 고정 포트로 하지 않고, 현재 게임이 실제로 열린 주소 기준으로 안전하게 계산한다.

기존 예시였던 `http://127.0.0.1:5500/admin.html`은 VS Code Live Server의 흔한 기본 포트일 뿐이다. 사용자의 로컬 환경에서는 `5501`, `5173`, 하위 경로가 붙은 주소 등으로 열릴 수 있다.

## 핵심 규칙

```txt
관리자 페이지 주소 = 현재 게임 주소와 같은 host/port/path 기준의 admin.html
```

예시:

```txt
게임: http://127.0.0.1:5501/index.html
관리자: http://127.0.0.1:5501/admin.html
```

```txt
게임: http://127.0.0.1:5500/Upgrade%20RPG/index.html
관리자: http://127.0.0.1:5500/Upgrade%20RPG/admin.html
```

## 추가된 브라우저 함수

```js
// 위치: 브라우저 개발자도구 Console
getAdminReadOnlyPageUrl();
copyAdminReadOnlyPageUrl();
openAdminReadOnlyPage();

getCurrentAdminPageUrl();
copyCurrentAdminPageUrl();
checkAdminReadOnlyPageReady();
```

## 변경 파일

- `src/api/admin-readonly-overview.js`
- `src/api/admin-page-readonly.js`
- `admin.html`
- `tools/smoke/frontend/smoke_admin_page_url_helper.js`
- `tools/smoke/frontend/smoke_admin_readonly_page.js`
- `tools/smoke/frontend/smoke_admin_readonly_overview.js`

## DB reset / seed

필요 없음.

프론트 관리자 페이지 링크/안내만 수정한다.
