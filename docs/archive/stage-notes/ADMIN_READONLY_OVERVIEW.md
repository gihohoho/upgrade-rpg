# v111 관리자 읽기 전용 overview

## 목적

관리자 페이지로 바로 쓰기 기능을 붙이면 사고 위험이 크기 때문에, v111에서는 먼저 **읽기 전용 overview API**와 브라우저 확인 모달만 추가했다.

이 단계는 DB/localStorage를 수정하지 않는다.

## 추가 API

```txt
GET /api/v1/admin/overview
GET /api/v1/admin/save-snapshots?limit=20
```

### `/admin/overview`

관리자 첫 화면에 필요한 요약 상태를 내려준다.

```txt
- 마스터 데이터 도메인별 row count
- 유저 수 요약
- DB 세이브 스냅샷 요약
- 관리자 UI 준비 상태
- 쓰기 UI 차단 사유
```

### `/admin/save-snapshots`

최근 세이브 스냅샷 목록을 조회한다.

안전장치:

```txt
- snapshot_json 원본은 내려주지 않는다.
- slotKey / saveVersion / summary / counts / updatedAt 같은 요약만 내려준다.
- readOnly=true를 명시한다.
```

## 브라우저 Console 함수

```js
// 위치: 브라우저 개발자도구 Console
await fetchAdminReadOnlyOverview();
await listAdminReadOnlySaveSnapshots();
await openAdminReadOnlyOverviewModal();
await checkAdminReadOnlyOverviewReady();
```

## SAVE DATA 배지

SAVE DATA 개발 배지에 `admin` 버튼을 추가했다.

```txt
SAVE DATA → admin
```

이 버튼은 관리자 준비 overview 모달만 열고, 게임 세이브/localStorage/DB를 수정하지 않는다.

## DB reset / seed 필요 여부

필요 없음.

이번 단계는 기존 테이블을 조회만 한다.

## 로컬 확인

백엔드 실행:

```bash
# 위치: backend 폴더 + 가상환경 activate 상태
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

API live 체크:

```bash
# 위치: backend 폴더 + 가상환경 activate 상태
python scripts/check_admin_readonly_api.py
```

정적 smoke:

```bash
# 위치: 프로젝트 루트
node tools/smoke_admin_readonly_overview.js
python tools/smoke_admin_readonly_api_structure.py
```

## 다음 단계 후보

```txt
1. 관리자 변경 미리보기 API를 실제 target별 검증으로 확장
2. admin_change_logs 기반 변경 이력 저장 준비
3. 읽기 전용 관리자 HTML/Vue 화면 초안 준비
4. 마스터 데이터 수정 API는 변경 이력/rollback 구조가 준비된 뒤 추가
```
