# Documentation System

## 목표

새 채팅이 짧은 시간 안에 현재 상태를 이해하고, 사람도 원하는 정보를 위치만 보고 찾을 수 있게 합니다. 같은 상태를 여러 파일에 복사하지 않습니다.

## 읽기 순서

1. 루트 `AGENTS.md`: 오래 유지되는 작업 규칙
2. 루트 `NEXT_CHAT_HANDOFF.md`: 현재 checkpoint와 바로 다음 행동
3. `current/CURRENT_STATUS.md`: 상세 구현·검증·승인 경계
4. 현재 작업에 직접 관련된 reference/contract/guide 한두 개
5. 과거 원인이 필요할 때만 `archive/history/` 검색

`NEXT_CHAT_PROMPT.md`는 위 세 문서를 알려주는 짧은 시작 안내이며 상태를 복제하지 않습니다.

## 파일 위치 규칙

| 위치 | 용도 | 직접 편집 |
|---|---|---|
| 루트 | 저장소 진입점과 Codex handoff | 가능 |
| `docs/current/` | 지금 판단·승인에 필요한 문서 | 가능 |
| `docs/reference/` | 계속 유효한 주제별 기술 자료 | 가능 |
| `docs/generated/` | 도구가 재생성하는 보고서 | 금지 |
| `docs/contracts/` | API·관리자 계약 | 가능 |
| `docs/guides/` | 사람이 따라 하는 실행 절차 | 가능 |
| `docs/archive/history/` | 완료 단계의 통합 역사 | 원칙적으로 읽기 전용 |

새 파일을 만들기 전에 기존 문서의 섹션으로 충분한지 확인합니다. current 문서가 더 이상 현재 판단에 필요하지 않으면 reference로 옮기고, 단계 메모는 주제별 history에 합칩니다.

## 중복 방지

- 현재 marker는 handoff와 current status에만 둡니다. prompt에는 복사하지 않습니다.
- 생성 보고서의 내용을 사람이 관리하는 문서에 통째로 복사하지 않고 링크합니다.
- 완료된 메모를 날짜·버전별 새 파일로 계속 늘리지 않습니다. 관련 history 문서에 원본 경로 제목과 함께 추가합니다.
- 같은 byte 내용의 Markdown 복사본을 만들지 않습니다.
- 문서 이동 시 repository 전체의 링크, checker, smoke, 배포 정적 계약을 함께 갱신합니다.

## 크기와 이름

- entry 문서는 빠르게 읽을 수 있게 유지합니다: `AGENTS.md`, handoff, current status는 각각 약 20KB 이하를 목표로 합니다.
- `docs/current/`는 약 20개 이하를 목표로 합니다.
- 파일명은 역할이 드러나는 대문자 snake case를 유지하되 단순 진행 버전만 다른 파일을 만들지 않습니다.
- 아주 긴 증거는 JSON/report 또는 archive history로 분리합니다.

## Obsidian 사용

Obsidian은 **선택형 로컬 뷰어**로만 사용합니다. 프로젝트 동작이나 Codex 품질이 Obsidian 설치 여부에 의존하면 안 됩니다.

1. Obsidian에서 새 빈 vault를 만들지 말고 **이 저장소 루트 폴더**를 기존 vault로 엽니다.
2. 내부 링크는 Obsidian 전용 wikilink보다 표준 Markdown 링크를 사용합니다.
3. 개인 workspace, plugin, appearance 설정인 `.obsidian/`은 Git에 올리지 않습니다.
4. 처음에는 community plugin 없이 검색, backlinks, graph만 사용합니다.
5. 문서 수정은 VS Code/Codex와 Obsidian 어느 쪽에서 해도 되지만 source of truth는 Git 파일입니다.

Obsidian은 탐색에는 도움이 되지만 파일 수와 중복을 스스로 해결하지는 않습니다. 이 저장소의 품질은 폴더 규칙과 자동 구조 검사로 유지합니다.
