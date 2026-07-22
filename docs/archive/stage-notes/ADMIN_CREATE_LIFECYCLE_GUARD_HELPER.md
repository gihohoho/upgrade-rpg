# Admin Create Lifecycle Guard Helper

현재 기준: **v181 admin create lifecycle guard helper**

## 목적

v181은 신규 row 생성·삭제·복원 기능을 더 열지 않고, 이미 열린 흐름을 브라우저에서 더 안전하게 확인하기 위한 보조 UI를 추가합니다.

## 추가 내용

- `createLifecycle` 메타데이터에 삭제 preview 차단 기준을 추가했습니다.
- 관리자 페이지 `신규 row 생성·삭제·복원 점검` 섹션에서 도메인별 삭제 차단 기준을 바로 볼 수 있습니다.
- 변경 이력 action 필터 바로가기 버튼을 추가했습니다.
  - `create` 이력 보기
  - `create_delete` 이력 보기
  - `create_delete_restore` 이력 보기
- `checkAdminReadOnlyPageReady()`에 `createLifecycleDependencyGuideReady` 상태를 추가했습니다.

## 삭제 차단 기준 표시

부모 성격의 도메인은 연결 데이터가 있으면 삭제 preview에서 차단됩니다.

예:

- `skills`는 `skillLevels`, `characterSkills`, `userCharacterSkills` 연결이 있으면 삭제 차단.
- `itemTemplates`는 `dropTableItems`, `itemInstances` 연결이 있으면 삭제 차단.
- `dropTables`는 `dropTableItems` 연결이 있으면 삭제 차단.

leaf 성격의 도메인은 현재값 일치 검사 후 id 기준 삭제/복원 흐름을 사용합니다.

예:

- `dropTableItems`
- `skillLevels`
- `enhancementLevels`
- `characterSkills`

## 안전성

- 새 쓰기 도메인 오픈 없음.
- DB schema 변경 없음.
- DB reset / seed 필요 없음.
- 실제 삭제/복원 판단은 기존 백엔드 preview가 계속 최종 결정합니다.
- 이번 UI는 위험한 DB 수정 없이 안내와 필터 편의만 제공합니다.

## 브라우저 확인

위치: 브라우저 개발자도구 Console

```js
checkAdminReadOnlyPageReady().version
```

예상 결과:

```txt
v181.admin-create-lifecycle-guard-helper
```

위치: 브라우저 개발자도구 Console

```js
checkAdminReadOnlyPageReady().createLifecycleDependencyGuideReady
```

예상 결과:

```txt
true
```
