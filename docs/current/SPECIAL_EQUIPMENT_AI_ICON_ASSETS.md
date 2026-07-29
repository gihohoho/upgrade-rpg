# Special Equipment AI Icon Assets — v360

## 생성 방식

- 생성 도구: Codex built-in `image_gen`
- use case: `stylized-concept`
- 대상: 64×64 슬롯에 축소되는 2D fantasy game UI icon
- 최종 파일: `src/assets/special-equipment/*.png`
- 최종 크기: 23 files / 각 256×256 PNG
- 공통 제한: 텍스트·숫자·캐릭터·로고·워터마크 없음, 실사보다 단순한 hand-painted/cel-painted 스타일, 짙은 남색 배경과 작은 슬롯에서도 읽히는 실루엣

## 최종 프롬프트 세트

### 특수무기·목걸이·반지

3행×4열 progression atlas. 같은 무기/목걸이/반지 실루엣을 유지하면서 기본 보라·강철 → 초월 인디고·은장 → 해방 청백 에너지·금장 → 짙은 흑보라 코어·청록 광채 순으로 강화합니다. 셀 간 겹침 없이 정면 inventory icon으로 생성합니다.

### 아바타 3종

3행×2열 progression atlas. 무기 아바타는 spectral sword, 오라 아바타는 circular magical crest, 클론 레어 아바타는 사람이 없는 armored costume torso로 표현합니다. 기본 은장·보라/파랑 → 찬란한 금장·청록/자홍 광채와 작은 sparkle 순으로 강화하며 같은 실루엣을 유지합니다.

### 탈리스만

1행×4열 progression atlas. 마름모 rune charm과 아래 ribbon 실루엣을 유지하면서 기본 은장 보라 → 초월 인디고·은빛 날개 장식 → 찬란한 자홍·금장 → 영롱한 청보라 crystal core·겹 halo 순으로 강화합니다.

### 휘장

단일 정면 emblem. 네 방향이 짧게 뻗은 원형 금빛 crest, 중앙 star crystal, 청보라 enamel, 아래 짧은 ribbon으로 구성합니다.

## 이름별 매핑

- 특수무기/목걸이/반지: `basic`, `transcendent`, `liberated`, `dark`
- 무기/오라/클론 레어 아바타: `basic`, `radiant`
- 탈리스만: `basic`, `transcendent`, `radiant`, `luminous`
- 휘장: `emblem.png`

`src/utils/icon-utils.js`가 장비 이름과 `specialSlotIdx`를 함께 판별합니다. 저장 데이터에 남아 있는 이전 placeholder URL은 로드 시 `normalizeSpecialStackItem()`이 새 경로로 교체합니다.
