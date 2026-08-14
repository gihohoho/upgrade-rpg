# Documentation System

## 목표

새 채팅이 짧은 시간 안에 현재 상태를 이해하고, 사람도 원하는 정보를 위치만 보고 찾을 수 있게 합니다. 같은 상태를 여러 파일에 복사하지 않습니다.

## 읽기 순서

1. 루트 [AGENTS.md](../AGENTS.md): 오래 유지되는 작업 규칙
2. 루트 [NEXT_CHAT_HANDOFF.md](../NEXT_CHAT_HANDOFF.md): 현재 checkpoint와 바로 다음 행동
3. [CURRENT_STATUS.md](current/CURRENT_STATUS.md): 상세 구현·검증·승인 경계
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

## 작업 종료 문서 마감

기능·버그·조사·설치·배포 준비 등 작업 종류와 관계없이 다음 순서로 마감합니다.

1. [AGENTS.md](../AGENTS.md), [NEXT_CHAT_HANDOFF.md](../NEXT_CHAT_HANDOFF.md), [CURRENT_STATUS.md](current/CURRENT_STATUS.md)를 현재 코드·검증·승인 경계와 맞춥니다. 장기 규칙이 그대로여도 checkpoint와 다음 행동이 낡지 않았는지 확인합니다.
2. 변경 주제와 관련된 Markdown을 `rg`로 전수 검색해 오래된 수치·경로·승인 문구를 갱신합니다.
3. 새 문서가 정말 필요한지 확인하고, 기존 섹션으로 충분하면 통합합니다. 끝난 단계 메모는 새 current 파일로 남기지 않고 관련 `archive/history/`에 합칩니다.
4. 이동·삭제 시 표준 Markdown 링크, checker, generated report source와 smoke를 함께 갱신합니다.
5. 문서 구조 smoke, handoff smoke, broken link·중복·크기 예산 검사를 통과시킨 뒤에만 commit합니다.

핵심 3문서는 모든 작업에서 확인하지만, 동일 내용을 채우기 위한 의미 없는 문장 추가나 날짜만 바꾸는 churn은 만들지 않습니다.

## Obsidian 사용

Obsidian 1.13.7은 이 프로젝트의 **로컬 지식 탐색기**로 사용합니다. 프로젝트 동작이나 Codex 품질이 Obsidian 설치 여부에 의존하면 안 되며, source of truth는 계속 Git의 표준 Markdown입니다.

1. 등록된 **`Upgrade RPG` vault**가 이 저장소 루트 폴더인지 확인해 엽니다. 새 빈 vault를 만들지 않습니다.
2. 내부 링크는 Obsidian 전용 wikilink보다 표준 Markdown 링크를 사용합니다.
3. 개인 workspace, plugin, appearance 설정인 `.obsidian/`은 Git에 올리지 않습니다. local 설정은 표준 Markdown 상대 링크, 자동 링크 갱신, 삭제 확인을 사용합니다.
4. File explorer, Search, Quick switcher, Bookmarks, Backlinks, Outgoing links, Outline, Page preview, Graph, Command palette, File recovery, Workspaces 같은 core plugin만 사용합니다. community plugin, Sync, Publish, Daily notes, Canvas, Bases, Properties, Tags는 현재 필요하지 않습니다.
5. 문서 수정은 VS Code/Codex와 Obsidian 어느 쪽에서 해도 되지만 source of truth는 Git 파일입니다.

### 뇌처럼 보이는 Graph의 의미

Graph View에서 원은 Markdown 문서, 선은 문서 사이의 실제 내부 링크입니다. 문서 내용을 AI가 자동으로 이해해서 연결하는 지식 그래프가 아니므로 링크가 없는 파일은 고립된 점으로 보입니다. 전체 Graph는 구조·고립 문서·과도하게 큰 중심 문서를 발견하는 지도에 가깝고, 평소 작업에는 현재 문서 주변만 보여주는 **Local Graph 깊이 2**가 더 실용적입니다.

### 이 프로젝트의 추천 사용 순서

1. Bookmarks에 `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`, `docs/README.md`를 등록합니다.
2. 전체 Graph의 filter에 아래 식을 넣고 `Existing files only`를 켜며 `Orphans`와 `Attachments`는 끕니다.
3. Graph group은 `path:"docs/current"`를 금색, `path:"docs/reference"`를 파란색, `path:"docs/archive/history"`를 회색으로 지정합니다.
4. 작업 문서에서는 Command Palette의 `Open local graph`를 열고 depth를 2로 둡니다. 관련 계약·상태·reference만 작은 뇌 모양으로 볼 수 있습니다.
5. 오른쪽 Backlinks에서 이 문서를 참조하는 다른 문서를 확인하고, `Unlinked mentions`는 빠진 링크 후보를 찾는 용도로만 사용합니다.
6. 아래 검색식을 Search에 입력한 뒤 자주 쓰는 검색 자체를 Bookmark합니다.

Obsidian의 local 검색 색인에서는 `.git/`, `.obsidian/`, `backend/.venv/`, `frontend/vue-app/node_modules/`, `frontend/legacy-dist/`, `local-backups/`, `local-review-artifacts/`, `.code-review-graph/`, `deploy/secrets/`를 제외합니다. `docs/archive/history/`는 과거 원인 검색에 필요하므로 제외하지 않고 Graph에서만 다음 filter로 숨길 수 있습니다.

```txt
-path:"docs/archive/history" -path:"docs/generated"
```

유용한 검색 예시는 다음과 같습니다.

```txt
path:"docs/current"
(path:"docs/current" OR path:"docs/reference" OR path:"docs/contracts" OR path:"docs/guides")
path:"docs/archive/history"
```

95개 문서에 YAML frontmatter, tag, alias를 일괄 추가하지 않습니다. 폴더가 lifecycle metadata 역할을 하고 있으며, 일괄 속성은 중복·stale 상태와 Codex 읽기 비용을 늘립니다. Obsidian에서 새 scratch note나 attachment를 무심코 만들지 않고, 새 Markdown은 위 파일 위치 규칙으로 먼저 분류합니다.

Obsidian은 탐색에는 도움이 되지만 파일 수와 중복을 스스로 해결하지는 않습니다. 이 저장소의 품질은 폴더 규칙과 자동 구조 검사로 유지합니다.
