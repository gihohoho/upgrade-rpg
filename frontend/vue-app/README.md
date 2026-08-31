# Upgrade RPG Vue App — v383

이 폴더는 Upgrade RPG 전체 프론트엔드를 Vue로 옮기는 작업공간입니다. 현재 공개 게임과 관리자 화면은 아직 루트 `index.html`, `admin.html`, legacy `src/`를 사용합니다.

## 현재 범위

- Vue 3 + Vite + Vue Router
- 새 Vue 코드 TypeScript
- Pinia 공통·계정·관리자 접근 상태
- 반응형 공통 layout과 접근성 기반
- `/game`: 로그인·가입·이메일 인증 안내와 계정별 캐릭터 슬롯 8개 gate
- `/admin`: `isAdmin=true` route guard 뒤 read-only 조회, 생성·수정·되돌리기 dry-run Preview, 실제 쓰기 없는 Apply 확인 준비
- `/admin/access`: 관리자 로그인·권한 거부·network 재시도

`/game`은 typed API client와 Pinia account store로 인증 token과 선택 캐릭터를 처리하지만, 실제 게임 boot·snapshot load·save는 이후 기능 단계까지 시작하지 않습니다. `/admin`은 관리자 권한 확인 전에는 컴포넌트를 렌더링하지 않으며 모든 관리자 GET/Preview에 Bearer를 사용합니다. Preview POST는 `dryRun: true`로 고정합니다. v383 확인 모달은 같은 Preview의 SHA-256 지문 재검증, 서버 확인 문구 일치, 현재 비밀번호·dev key 입력 경계까지만 준비하며 Apply API나 DB write에는 연결하지 않습니다. 민감 입력은 브라우저 저장소·로그·네트워크에 남기지 않고 모달 종료 시 지웁니다.

## 설치와 실행

실행 위치: `frontend/vue-app`

Python `.venv`: 필요 없음

```bash
npm ci
npm run dev
```

확인 주소:

```txt
http://127.0.0.1:5173/game
http://127.0.0.1:5173/admin
```

## 검사와 빌드

```bash
npm run typecheck
npm run build
```

`npm run build`는 먼저 TypeScript 검사를 실행한 뒤 Vite production bundle을 만듭니다.
