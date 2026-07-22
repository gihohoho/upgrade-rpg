# CSS 점검 보고서

## 점검 대상

```txt
src/styles/style.css
```

## 요약 결론

현재 CSS는 같은 클래스/선택자가 여러 곳에서 반복됩니다.
다만 전부 버그라고 보기는 어렵고, 일부는 아래 목적의 의도된 누적 스타일입니다.

```txt
기본 스타일 정의
특정 패널에서만 덮어쓰기
버전별 추가 패치
모바일/하단 HUD 보정
토글 ON/OFF 상태 보정
```

하지만 파일이 커진 상태라서 유지보수성은 떨어지고 있습니다.

## 검사 결과

단순 선택자 기준 검사 결과:

```txt
전체 선택자 수: 약 535개
고유 클래스 수: 약 231개
2회 이상 등장한 클래스 수: 약 105개
완전히 같은 선택자가 2회 이상 등장한 항목: 약 93개
```

많이 반복되는 클래스 예시:

```txt
damage-text: 21회
inv-header: 12회
town-hub-btn: 11회
gold-box: 10회
item-slot: 9회
unique-stat-row: 9회
skill-slots-grid: 8회
sys-btn: 8회
inv-grid-50: 7회
action-btn: 6회
```

완전히 같은 선택자가 여러 번 등장하는 예시:

```txt
#item-action-panel
#mailbox-panel
#trash-panel
#inv-panel
#storage-panel
.gold-box
.hud-center-stats
.action-btns
.hud-sys-btns
```

## 주의해서 볼 부분

### 1. `.skill-slots-grid`

여러 위치에서 반복됩니다.

```txt
기본 그리드
스킬 슬롯 wrapper
쿨타임 텍스트
하단 HUD 보정
추가 패치
```

현재 게임이 정상 동작한다면 바로 합치기보다, 스킬 UI를 Vue 컴포넌트로 옮길 때 함께 정리하는 것이 안전합니다.

### 2. `.sys-btn`

기본 버튼 스타일과 테스트 패널/아이템 리스트/토글 상태 스타일이 섞여 있습니다.

관리자 페이지까지 고려하면 나중에 아래처럼 분리하는 게 좋습니다.

```txt
.btn
.btn--system
.btn--test
.btn--toggle
.btn--danger
.btn--primary
```

### 3. 패널 ID 선택자

아래 선택자들이 여러 번 반복됩니다.

```txt
#inv-panel
#storage-panel
#trash-panel
#mailbox-panel
#item-action-panel
```

패널 공통 스타일을 하나로 묶고, 각 패널 차이만 별도 클래스로 빼는 게 좋습니다.

예상 구조:

```txt
.panel
.panel--inventory
.panel--storage
.panel--trash
.panel--mailbox
.panel--action
```

## SCSS로 바꾸는 게 좋을까?

현재 단계에서는 바로 SCSS로 바꾸는 것보다 **CSS 유지 + 구조 정리 문서화**가 더 안전합니다.

이유:

```txt
현재 프로젝트는 아직 Vite/Vue 빌드 환경이 아닙니다.
SCSS를 쓰려면 빌드 도구가 필요합니다.
지금은 index.html에서 CSS를 직접 불러오는 구조입니다.
백엔드 분리 준비 중이라 CSS 빌드 환경까지 동시에 바꾸면 테스트 범위가 커집니다.
```

## 추천 방향

### 지금 당장

```txt
CSS 유지
중복 선택자 위치 문서화
위험한 통합은 보류
```

### 다음 정리 단계

```txt
style.css를 기능별 CSS 파일로 나누기
예: base.css, layout.css, hud.css, inventory.css, combat.css, modal.css, admin.css
```

### Vue/Vite로 넘어갈 때

그때 SCSS 도입을 추천합니다.

```txt
Vue/Vite 전환 후 SCSS 사용 추천
컴포넌트별 scoped style 또는 SCSS partial 사용
변수, mixin, 공통 버튼 스타일 관리
```

## 최종 판단

```txt
지금: CSS 유지가 좋음
중기: CSS 파일 분리 추천
Vue/Vite 전환 후: SCSS 도입 추천
```

## 중복 선택자 정리 원칙

현재 CSS에는 같은 클래스명 또는 같은 선택자가 여러 번 등장합니다. 다만 아래 두 개는 의미가 다릅니다.

```txt
2회 이상 등장한 클래스 수
→ 같은 클래스명이 여러 문맥에서 쓰인다는 뜻입니다.
→ 예: .item-slot, .gold-box 등이 기본/상태/미디어쿼리/자식 선택자에서 반복될 수 있습니다.
→ 이것만 보고 하나로 합치면 위험합니다.

완전히 같은 선택자가 2회 이상 등장한 항목
→ 선택자 문자열 자체가 같은 규칙이 여러 번 선언되었다는 뜻입니다.
→ 이 항목은 병합 후보가 맞지만, 뒤쪽 선언이 앞쪽 선언을 덮어쓰는 의도일 수 있어서 값 비교 후 선별 병합해야 합니다.
```

권장 순서:

```txt
1. 완전히 같은 선택자 + 충돌 없는 속성부터 병합
2. 같은 클래스지만 상태/반응형/자식 선택자가 다른 규칙은 유지
3. Vue/Vite 전환 전까지는 SCSS 전환보다 CSS 파일 분리를 우선
4. SCSS는 Vue 전환 후 도입
```



## v070 추가 정리 결과

`style.css`에서 최종 CSS 적용값이 유지되는 것으로 검증된 안전 중복 규칙만 병합했습니다.

```txt
병합/제거한 안전 중복 규칙: 38개
영향을 받은 선택자 그룹: 30개
병합 후 완전 동일 중복 블록: 0개
남은 중복 선택자: 55개
```

남은 중복 선택자는 cascade 순서, 상태별 스타일, 향후 CSS 파일 분리 가능성을 고려해 이번 작업에서는 유지했습니다. 자세한 기준은 `docs/archive/stage-notes/CSS_MERGE_REPORT.md`를 참고하세요.
