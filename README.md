# Upgrade RPG v192 패키지

현재 안정 버전: **v192 admin master catalog/detail split**

새 채팅 인수인계 ZIP: **rpg_v192_admin_master_catalog_split_ready.zip**

## 요약

v192에서는 관리자 `master catalog/detail` 구현을 실제 외부 JS 파일로 1차 분리했습니다.

새 파일:

- `src/api/admin/admin-master-catalog.js`

기존 호환 wrapper는 `src/api/admin-page-readonly.js`에 유지했습니다.

## 현재 관리자 JS 분리 상태

- `src/api/game-api-client.js` — 기존 외부 API client
- `src/api/admin-layout-shell.js` — v185 분리 완료
- `src/api/admin/admin-change-logs.js` — v187 분리 완료
- `src/api/admin/admin-create-lifecycle.js` — v189.1 hotfix 포함 분리 완료
- `src/api/admin/admin-edit-draft.js` — v191 분리 완료
- `src/api/admin/admin-master-catalog.js` — v192 분리 완료
- `src/api/admin-page-readonly.js` — bootstrap/bindEvents/window wrapper 중심 entry 파일

## v192에서 분리한 기능

- 마스터 카탈로그 필터 읽기/초기화/설명
- 도메인 옵션 동기화
- 마스터 카탈로그 테이블 렌더링
- 카탈로그 페이지네이션
- 선택 row 표시
- 마스터 상세 렌더링/열기
- code 기반 relation 대상 열기
- 실제 연결 항목 렌더링/조회
- `/game/master-data` API 반영 확인
- DB write 이후 자동 API 반영 확인

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상값:

```txt
v192.admin-master-catalog-detail-split
```

```js
checkAdminReadOnlyPageReady().masterCatalogExternalReady
```

예상값:

```txt
true
```

```js
window.RpgAdminMasterCatalog.VERSION
```

예상값:

```txt
v192.admin-master-catalog-detail-split
```

## 검증

- `bash tools/run_smoke_core.sh` 통과
- `node --check` 주요 관리자 JS 통과
- `python -m compileall -q backend/app` 통과

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음

## 다음 추천 단계

다음 v193은 **admin overview/snapshot 분리**가 좋습니다.

후보 파일:

```txt
src/api/admin/admin-overview-snapshots.js
```

추천 분리 범위:

- overview cards
- snapshot filters
- snapshot table
- snapshot pagination/metadata가 있다면 함께 이동
