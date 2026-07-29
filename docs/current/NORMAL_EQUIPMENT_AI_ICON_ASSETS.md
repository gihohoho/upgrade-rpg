# 일반 장비 AI 아이콘 계열 계획 — v363

## 목표와 현재 진행

- 대상: 일반 보스 1~39단계의 일반 장비 195개
- 계열 판정 후 필요한 고유 PNG: 115개
- v363 완료: 10~20단계 장비 55개를 덮는 고유 PNG 15개
- 남은 PNG: 100개
- 다음 묶음: 1~9단계
- 최종 파일 위치: `src/assets/equipment/*.png`
- 파일 규격: 모두 256×256 PNG

## 같은 장비 계열 판정

다음 승급 표식만 이름 앞에서 제거합니다.

```txt
-현-
-진-
-초월-
★심연★
★연옥★
★진 연옥★
★초월 연옥★
```

표식을 제거한 이름이 정확히 같을 때만 같은 PNG를 공유합니다. 예를 들어 `마음을 새긴 바다`, `-진- 마음을 새긴 바다`, `★심연★ 마음을 새긴 바다`는 하나의 이미지 계열입니다.

반대로 `절망 : 티아매트의 불신`과 `끝없는 절망 : 티아매트의 불신`, `파멸 : 베리아스의 불신`과 `영원한 파멸 : 베리아스의 불신`은 이름 자체가 달라지므로 현재 규칙에서는 별도 계열입니다. 시각적으로 관련 있어 보여도 자동으로 같은 이미지라고 추측하지 않습니다.

## 1~39단계 계열 분류

| 단계 | 이미지 계열 | 상태 |
|---|---|---|
| 1 | 단독 5개 | 예정 |
| 2 | 단독 5개 | 예정 |
| 3 | 단독 5개 | 예정 |
| 4 | 단독 5개 | 예정 |
| 5 | 단독 5개 | 예정 |
| 6, 8 | 6단계 기본 이름 5개 공유 (`-현-`) | 예정 |
| 7, 9 | 7단계 기본 이름 5개 공유 (`-초월-`) | 예정 |
| 10, 11, 12, 18, 19, 20 | 10단계 기본 이름 5개 공유 (`-진-`, `-초월-`, 연옥 3단계) | v363 완료 |
| 13, 14, 15 | 13단계 기본 이름 5개 공유 (`-진-`, `★심연★`) | v363 완료 |
| 16, 17 | 16단계 기본 이름 5개 공유 (`-진-`) | v363 완료 |
| 21, 22 | 21단계 기본 이름 5개 공유 (`-진-`) | 예정 |
| 23 | `끝없는 절망` 단독 5개 | 예정 |
| 24, 25 | 24단계 기본 이름 5개 공유 (`-진-`) | 예정 |
| 26 | `영원한 파멸` 단독 5개 | 예정 |
| 27, 28 | 27단계 기본 이름 5개 공유 (`-진-`) | 예정 |
| 29 | 단독 5개 | 예정 |
| 30, 31 | 30단계 기본 이름 5개 공유 (`-진-`) | 예정 |
| 32 | 단독 5개 | 예정 |
| 33 | 단독 5개 | 예정 |
| 34 | 단독 5개 | 예정 |
| 35, 36 | 35단계 기본 이름 5개 공유 (`-진-`) | 예정 |
| 37, 38 | 37단계 기본 이름 5개 공유 (`-진-`) | 예정 |
| 39 | 단독 5개 | 예정 |

## v363 파일 매핑

| 기본 장비 이름 | 파일 |
|---|---|
| 어둠을 지배하는 고리 | `dark-dominion-ring.png` |
| 올 엘리멘탈 크리스탈 | `all-elemental-crystal.png` |
| 군신의 가호가 담긴 보석 | `war-god-blessing-jewel.png` |
| 루나 베네딕티오 | `luna-benedictio.png` |
| 영창 : 불멸의 혼 | `immortal-soul-chant.png` |
| 마음을 새긴 바다 | `engraved-sea-heart.png` |
| 종말의 시간 | `time-of-end.png` |
| 광란을 품은 자 | `embracing-frenzy.png` |
| 세계수의 뿌리 | `world-tree-root.png` |
| 어나이얼레이터 | `annihilator.png` |
| 무의식 : 넥스의 몽환의 어둠 | `nex-dream-darkness.png` |
| 환영 : 넥스의 검은 기운 | `nex-black-energy.png` |
| 환영 : 넥스의 잠식된 의복 | `nex-corrupted-garment.png` |
| 원초의 꿈 : 스태프 | `primal-dream-staff.png` |
| 원초의 꿈 : 창 | `primal-dream-spear.png` |

## 공통 생성 프롬프트

기본 built-in `image_gen`을 사용했으며 API 키나 새 dependency는 사용하지 않았습니다.

```txt
Use case: stylized-concept
Asset type: square game UI equipment icon
Style/medium: simple hand-painted 2D icon for a Korean side-scrolling fantasy action RPG; bold readable silhouette; compact forms; minimal detail; restrained shading
Composition/framing: exact 1:1 square; one object in a close crop, centered and large enough to fill about 85% of the canvas; recognizable even at 64px
Scene/backdrop: simple full-bleed very dark navy gradient backdrop, no card panel
Constraints: no text, no letters, no numbers, no logo, no watermark, no frame, no border, no built-in rarity decoration; keep the entire design simple rather than ornate; use only 2 or 3 dominant colors; no particles, no wings, no excessive glow, no complex filigree
```

각 파일에는 위 공통 프롬프트 뒤에 표의 장비를 직관적으로 나타내는 단일 물체 설명을 붙였습니다. 예를 들면 `마음을 새긴 바다`는 푸른 하트형 조개 펜던트, `종말의 시간`은 금이 간 회중시계, `원초의 꿈 : 창`은 은색·보라색 잎 모양 창으로 생성했습니다.

## CSS 승급 표현

같은 계열은 이미지 자체를 다시 화려하게 만들지 않습니다.

```txt
기본: basic 흰색
-현-: uncommon 녹색
-진-: rare 파란색
-초월-: transcendent 청록색
★연옥★: radiant 분홍·청록
★진 연옥★ / ★심연★: dark 보라
★초월 연옥★: luminous 다색
```

모든 등급은 장착칸, 가방, 보관함, 휴지통, 관리창과 지급 미리보기에서 같은 `getItemFrameGrade()` 판정을 사용합니다.

## 검증

- `tools/smoke/game/smoke_equipment_icon_families.js`
  - 10~20단계 일반 장비 55개
  - 로컬 이미지 적용 55/55
  - 고유 계열 이미지 15개
  - `마음을 새긴 바다`·연옥 계열 이름/이미지/등급 공유
  - 15개 PNG signature와 256×256 크기
- `tools/smoke/frontend/smoke_legacy_static_deployment_preparation.js`
  - 정적 배포 산출물에 특수장비 23개와 일반 장비 15개가 모두 포함되는지 검사

장비 능력치, 강화 공식, 드롭률, backend API/image, Neon DB와 Render 서비스는 변경하지 않았습니다.
