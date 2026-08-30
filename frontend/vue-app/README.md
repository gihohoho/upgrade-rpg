# Upgrade RPG Vue App — v380

이 폴더는 Upgrade RPG 전체 프론트엔드를 Vue로 옮기는 작업공간입니다. 현재 공개 게임과 관리자 화면은 아직 루트 `index.html`, `admin.html`, legacy `src/`를 사용합니다.

## 현재 범위

- Vue 3 + Vite + Vue Router
- 새 Vue 코드 TypeScript
- Pinia 공통·계정 상태
- 반응형 공통 layout과 접근성 기반
- `/game`: 로그인·가입·이메일 인증 안내와 계정별 캐릭터 슬롯 8개 gate
- `/admin`: 기존 read-only 도메인·카탈로그·상세·관계 조회

`/game`은 typed API client와 Pinia account store로 인증 token과 선택 캐릭터를 처리하지만, 실제 게임 boot·snapshot load·save는 이후 기능 단계까지 시작하지 않습니다. 관리자 write도 기존 보안·확인 계약과 함께 별도로 옮깁니다.

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
