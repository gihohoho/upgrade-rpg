# state 폴더 안내

이 폴더는 현재 게임 상태를 담당합니다.

## 핵심 파일

```txt
game-state.js
```

## 상태 구분

```txt
gameState.server
```

서버/DB에 저장할 값입니다.

```txt
gameState.client
```

화면에서만 필요한 값입니다.

```txt
gameState.runtime
```

전투 중 임시 상태처럼 실행 중에만 필요한 값입니다.

## 다음 목표

나중에 FastAPI 저장 API를 만들 때는 `gameState.server`만 전송하면 됩니다.

```txt
POST /game/save
GET /game/load
```
