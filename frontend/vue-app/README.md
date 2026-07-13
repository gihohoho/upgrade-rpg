# Upgrade RPG Vue App Shell — v270

이 폴더는 기존 게임/관리자 화면을 바로 대체하지 않는 Vue 기본 shell입니다.

현재 실제 화면은 계속 아래 legacy 파일이 담당합니다.

- 게임: 루트 `index.html`
- 관리자: 루트 `admin.html`
- legacy JS/CSS: 루트 `src/`

## 왜 `frontend/vue-app/`에 만들었나?

루트 `src/`는 이미 legacy 게임과 관리자 페이지가 직접 읽고 있습니다.
Vue/Vite도 기본적으로 `src/` 폴더를 사용하므로, 루트에 바로 Vue를 만들면 기존 구조와 충돌할 수 있습니다.
그래서 Vue 앱은 `frontend/vue-app/`에 분리했습니다.

## 이번 v270에서 만든 것

- Vite + Vue 기본 설정 파일
- Vue Router 기본 shell
- `/game` 화면: 게임 이식 준비 화면
- `/admin` 화면: 관리자 이식 준비 화면
- 실제 관리자/게임 로직 연결은 아직 하지 않음

## 사용자가 설치해야 하는 것

아직 ZIP에는 `node_modules`가 포함되어 있지 않습니다.
처음 실행할 때 한 번만 설치가 필요합니다.

실행 위치: `frontend/vue-app` 폴더

```bash
npm install
```

## 개발 서버 실행

실행 위치: `frontend/vue-app` 폴더

```bash
npm run dev
```

브라우저에서 아래 주소를 엽니다.

```txt
http://127.0.0.1:5173
```

## 빌드 확인

실행 위치: `frontend/vue-app` 폴더

```bash
npm run build
```

## 주의

v270은 shell 단계입니다.

아래는 변경하지 않았습니다.

- DB
- env
- seed
- 인증
- 기존 route path
- 기존 API 응답 body
- Write Guard
- 실제 write 로직
- 관리자 Preview/Apply 요청 body
- 기존 smoke/contract 의미
