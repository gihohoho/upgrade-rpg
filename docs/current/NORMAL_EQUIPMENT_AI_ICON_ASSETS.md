# 일반 장비 AI 아이콘 계열 계획 — v364

## 목표와 현재 진행

- 대상: 일반 보스 1~39단계의 일반 장비 195개
- 최종 목표: 장비별 별도 PNG 195개
- v364 최종 화풍·단계 발전 완료: `어둠을 지배하는 고리` 계열 6개
- 임시 기존 이미지: 나머지 10~20단계 계열 기본 PNG 14개
- 다음 묶음: 10·11·12·18·19·20단계의 나머지 4계열 24개
- 최종 파일 위치: `src/assets/equipment/*.png`
- 파일 규격: 모두 256×256 PNG

## 같은 장비 계열 판정

다음 승급 표식은 이름 앞에서 제거합니다.

```txt
-현-
-진-
-초월-
★심연★
★연옥★
★진 연옥★
★초월 연옥★
```

표식을 제거한 이름이 같으면 같은 계열입니다. 예를 들어 `마음을 새긴 바다`, `-진- 마음을 새긴 바다`, `★심연★ 마음을 새긴 바다`는 하나의 이미지 계열입니다.

승급 표식이 없어도 더 긴 상위 이름 안에 기본 장비 이름 전체가 들어 있으면 같은 계열입니다. 따라서 `절망 : 티아매트의 불신`·`끝없는 절망 : 티아매트의 불신`과 `파멸 : 베리아스의 불신`·`영원한 파멸 : 베리아스의 불신`은 각각 같은 계열입니다. 여러 기본 이름이 포함될 때는 가장 긴 이름을 우선합니다.

같은 계열이라는 것은 PNG를 공유한다는 뜻이 아닙니다. 계열 안의 모든 승급 단계는 각각 별도 PNG를 사용하되 기본 물체의 실루엣, 카메라 각도, 구도와 주요 부품을 유지하며 재질·색·장식·마력 효과만 발전시킵니다.

## 1~39단계 계열 분류

| 단계 | 이미지 계열 | 상태 |
|---|---|---|
| 1 | 단독 5개 | 예정 |
| 2 | 단독 5개 | 예정 |
| 3 | 단독 5개 | 예정 |
| 4 | 단독 5개 | 예정 |
| 5 | 단독 5개 | 예정 |
| 6, 8 | 6단계 기본 이름 5계열, 단계별 별도 이미지 (`-현-`) | 예정 |
| 7, 9 | 7단계 기본 이름 5계열, 단계별 별도 이미지 (`-초월-`) | 예정 |
| 10, 11, 12, 18, 19, 20 | 10단계 기본 이름 5계열, 단계별 6개 (`-진-`, `-초월-`, 연옥 3단계) | 반지 계열 6개 v364 완료 |
| 13, 14, 15 | 13단계 기본 이름 5계열, 단계별 3개 (`-진-`, `★심연★`) | 재생성 예정 |
| 16, 17 | 16단계 기본 이름 5계열, 단계별 2개 (`-진-`) | 재생성 예정 |
| 21, 22, 23 | 21단계 기본 이름 5계열, 단계별 3개 (`-진-`, `끝없는 `) | 예정 |
| 24, 25, 26 | 24단계 기본 이름 5계열, 단계별 3개 (`-진-`, `영원한 `) | 예정 |
| 27, 28 | 27단계 기본 이름 5계열, 단계별 2개 (`-진-`) | 예정 |
| 29 | 단독 5개 | 예정 |
| 30, 31 | 30단계 기본 이름 5계열, 단계별 2개 (`-진-`) | 예정 |
| 32 | 단독 5개 | 예정 |
| 33 | 단독 5개 | 예정 |
| 34 | 단독 5개 | 예정 |
| 35, 36 | 35단계 기본 이름 5계열, 단계별 2개 (`-진-`) | 예정 |
| 37, 38 | 37단계 기본 이름 5계열, 단계별 2개 (`-진-`) | 예정 |
| 39 | 단독 5개 | 예정 |

## v364 단계별 파일 매핑

`어둠을 지배하는 고리`는 같은 실루엣과 각도를 유지하면서 단계별 별도 이미지 6개로 완성했습니다.

| 단계 | 파일 |
|---|---|
| 기본 | `dark-dominion-ring.png` |
| `-진-` | `dark-dominion-ring-jin.png` |
| `-초월-` | `dark-dominion-ring-transcendent.png` |
| `★연옥★` | `dark-dominion-ring-purgatory.png` |
| `★진 연옥★` | `dark-dominion-ring-true-purgatory.png` |
| `★초월 연옥★` | `dark-dominion-ring-transcendent-purgatory.png` |

다음 14개는 v363의 임시 기본 이미지이며, 이후 묶음에서 같은 방식의 단계별 별도 PNG로 교체합니다.

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
Style/medium: crisp hand-painted cartoon/cel-shaded 2D icon for a Korean side-scrolling fantasy action RPG; bold dark contour; chunky readable silhouette; saturated gem colors; sharp metallic highlights
Composition/framing: exact 1:1 square; one object in a close crop, centered and large enough to fill about 90-94% of the canvas; recognizable even at 64px
Scene/backdrop: simple full-bleed very dark navy gradient backdrop, no card panel
Constraints: no text, no letters, no numbers, no logo, no watermark, no frame, no border, no built-in rarity decoration; allow 2-3 purposeful ornaments and controlled magic effects; no unrelated wings, no excessive particles, no glow that hides the object
```

각 파일에는 위 공통 프롬프트 뒤에 표의 장비를 직관적으로 나타내는 단일 물체 설명을 붙였습니다. 예를 들면 `마음을 새긴 바다`는 푸른 하트형 조개 펜던트, `종말의 시간`은 금이 간 회중시계, `원초의 꿈 : 창`은 은색·보라색 잎 모양 창으로 생성했습니다.

## 이미지와 CSS의 승급 표현

같은 계열의 이미지도 단계마다 별도로 발전시키고, CSS 테두리는 그 위에 공통 등급 정보를 추가로 보여줍니다.

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
  - `어둠을 지배하는 고리` 계열 6단계에 서로 다른 정확한 파일 적용
  - 나머지 미생성 계열은 기존 기본 이미지 fallback 유지
  - 20개 PNG signature와 256×256 크기
- `tools/smoke/frontend/smoke_legacy_static_deployment_preparation.js`
  - 정적 배포 산출물에 특수장비 23개와 일반 장비 20개가 모두 포함되는지 검사

장비 능력치, 강화 공식, 드롭률, backend API/image, Neon DB와 Render 서비스는 변경하지 않았습니다.
