# Handoff Cleanup Notes — v234

새 채팅으로 넘기기 전에 정리한 내용입니다.

## 문서 정리

- `NEXT_CHAT_PROMPT.md`를 새 채팅용 상세 프롬프트로 재작성했습니다.
- `NEXT_CHAT_HANDOFF.md`를 v234 기준으로 재작성했습니다.
- `README.md`와 `README_BACKEND_READY.md`를 v234 기준으로 갱신했습니다.
- `docs/CURRENT_STATUS.md`, `docs/NEXT_STEPS.md`, `docs/PROJECT_STRUCTURE.md`, `docs/README.md`의 오래된 v216/v217 안내를 v234 기준으로 정리했습니다.
- `docs/CHANGELOG.md` 상단에 v234 변경 기록을 추가했습니다.

## 삭제/제외한 것

- 패키징 전에 `__pycache__`, `.pyc`, 임시 로그/캐시류는 제외했습니다.
- `/mnt/data/rpg_v*_work` 같은 이전 채팅 작업용 임시 폴더는 새 zip에 포함하지 않았습니다.
- `.env`, `.git`, `.venv`, `node_modules`는 포함하지 않았습니다.

## 코드 구조 상태

이번 handoff 패키지에서는 기능 코드 동작을 바꾸지 않았습니다. 현재 안정판 v234 코드와 smoke 계약은 유지하고, 새 채팅 인수인계에 필요한 문서/정리만 반영했습니다.
