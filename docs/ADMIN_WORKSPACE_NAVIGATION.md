# Admin Workspace Navigation

## 목적

관리자 페이지가 기능 누적으로 길고 난잡해진 문제를 줄이기 위해, 기존 기능을 삭제하지 않고 상단에 업무 중심 진입점을 추가했습니다.

## 추가된 업무 모드

1. 조회·상세 확인
2. 신규 row 생성
3. 편집·적용 검토
4. Preview 화면 점검
5. 변경 이력·Rollback

## 동작 방식

- 업무 카드를 누르면 관련 섹션만 펼쳐집니다.
- 확인 순서, 주의사항, 주로 볼 버튼을 모달로 보여줍니다.
- 사이드바에도 같은 업무 모드 바로가기를 제공합니다.
- 전체 보기와 보조 섹션 접기 버튼으로 화면 밀도를 조절할 수 있습니다.

## 안전 범위

이 작업은 화면 구조와 안내 흐름만 추가합니다.

변경하지 않은 항목:

- DB
- env
- seed
- 인증
- route path
- API 응답 body
- Write Guard
- 실제 write 로직

`admin-workspace-navigation.js`는 `fetch`, `RpgGameApi`, `applyAdmin*`를 호출하지 않습니다.

## 검증

실행 위치: 프로젝트 루트

```bash
node tools/smoke/frontend/smoke_admin_workspace_navigation.js
```

전체 검증:

```bash
bash tools/run_smoke_core.sh
python -m compileall -q backend/app backend/scripts tools
```
