# 초보자 무기·스킬강화권·검신 스킬 AI 아이콘 — v369

## 적용 범위

v369에서는 기존 글자 placeholder를 다음 21개의 서로 다른 256×256 PNG로
교체합니다.

- 초보자 무기 `리버레이션 스태프`: 1장
- 스킬강화권 `Q → W → E → R → T → F → D → SQ → SW → M`: 10장
- 현재 기본 캐릭터 검신(`weapon_master`) 스킬: 10장
- v369 자산 URL 캐시 식별자: `?v=369`

장비 능력치, 강화 공식, 스킬 수치, 발동 확률, 전투 로직과 저장 데이터 구조는
변경하지 않습니다. 공개 Render Static Site도 계속 v351이며 이번 로컬 자산을
배포하지 않습니다.

## 프로젝트 최종 파일

초보자 무기는 다음 파일을 사용합니다.

```txt
src/assets/equipment/liberation-staff.png
```

스킬강화권은 다음 파일을 사용합니다.

| 순서 | 대응 슬롯 | 파일 |
|---:|---|---|
| 1 | Q | `src/assets/skill-books/skill-book-q.png` |
| 2 | W | `src/assets/skill-books/skill-book-w.png` |
| 3 | E | `src/assets/skill-books/skill-book-e.png` |
| 4 | R | `src/assets/skill-books/skill-book-r.png` |
| 5 | T | `src/assets/skill-books/skill-book-t.png` |
| 6 | F | `src/assets/skill-books/skill-book-f.png` |
| 7 | D | `src/assets/skill-books/skill-book-d.png` |
| 8 | SQ | `src/assets/skill-books/skill-book-sq.png` |
| 9 | SW | `src/assets/skill-books/skill-book-sw.png` |
| 10 | M | `src/assets/skill-books/skill-book-m.png` |

검신 스킬은 캐릭터 전용 폴더를 사용합니다.

| 슬롯 | 현재 스킬 | 색 계열 | 파일 |
|---|---|---|---|
| Q | 광검 마스터리 | 초록색 자동·패시브 | `src/assets/skills/weapon-master/q-lightsabre-mastery.png` |
| W | 극 귀검술 - 참철식 | 초록색 자동·패시브 | `src/assets/skills/weapon-master/w-iron-cutting.png` |
| E | 오버 드라이브 | 파란색 버프 | `src/assets/skills/weapon-master/e-overdrive.png` |
| R | 발도 | 초록색 자동 발동 | `src/assets/skills/weapon-master/r-quick-draw.png` |
| T | 환영검무 | 초록색 자동 발동 | `src/assets/skills/weapon-master/t-illusion-sword.png` |
| F | 극 귀검술 - 심검 | 초록색 자동 발동 | `src/assets/skills/weapon-master/f-mind-sword.png` |
| D | 극 귀검술 - 폭풍식 | 초록색 자동 발동 | `src/assets/skills/weapon-master/d-tempest.png` |
| SQ | 극 귀검술 - 유성락 | 보라색 강화 스킬 | `src/assets/skills/weapon-master/sq-meteor-fall.png` |
| SW | 극 발검술 - 무형참 | 보라색 강화 스킬 | `src/assets/skills/weapon-master/sw-formless-slash.png` |
| M | 천제극섬 | 보라색 진각성 스킬 | `src/assets/skills/weapon-master/m-heavenly-flash.png` |

현재 검신은 사용자가 직접 누르는 기본 액티브 스킬이 없습니다. 따라서
`Q`·`W`·`R`·`T`·`F`·`D`는 전투 중 자동 발동하거나 상시 적용되는 스킬로 보고
초록색 계열을 사용하며, `E`만 파란색 버프로 구분합니다.

## 이미지 제작 규칙

### 공통 규격

- 최종 파일은 정확한 1:1 정사각형 256×256 PNG입니다.
- 이미지 자체에는 카드, inset panel, 안쪽 프레임, 희귀도 테두리, margin band를
  넣지 않고 화면을 여백 없이 채웁니다.
- 글자, 슬롯 키, 숫자, 스킬명, 로고, 워터마크를 이미지에 넣지 않습니다.
- 키와 이름, 레벨과 수치는 UI가 별도로 표시합니다.
- 아이템 희귀도 테두리는 이미지와 합치지 않고 기존 게임의 CSS 프레임을
  장착칸·가방·보관함·휴지통 등 모든 표시 위치에서 적용합니다.

### 스킬 아이콘

- 사용자가 제시한 작은 스킬 슬롯 예시를 체감상 95% 이상 가깝게 따르는 것을
  목표로, 어두운 배경 위에 굵고 단순한 단일 문양 또는 동작 실루엣을 크게
  배치합니다.
- 작은 슬롯에서 즉시 알아볼 수 있도록 중심 동작과 무기 궤적만 남기고 복잡한
  배경·과도한 입자·세밀한 장식을 피합니다.
- 기본 자동·패시브는 초록색, 기본 버프는 파란색, 기본 액티브는 노란색입니다.
- `SQ`·`SW`·`M` 강화·진각성 스킬은 버프·패시브·액티브 구분 없이 보라색입니다.
- 추후 새 캐릭터를 추가하면 같은 `Q`·`W` 등의 슬롯이라도 검신 PNG를 공유하지
  않고 그 캐릭터의 동작과 정체성을 담은 별도 파일을 만듭니다.

### 스킬강화권 발전 순서

`Q`를 계열의 기본형으로 만들고 `W`, `E`, `R`, `T`, `F`, `D`, `SQ`, `SW`, `M`은
항상 바로 전 단계 PNG를 편집 원본으로 사용합니다. 모든 단계에서 같은 책·강화권의
정체성, 실루엣, 카메라 각도, 화면 배치와 중심 문양을 유지합니다. 단계가 오를수록
재질, 기존 부품의 장식, 룬과 절제된 마력 효과만 점진적으로 발전시키며 전혀 다른
물체로 다시 그리지 않습니다.

초보자 무기와 향후 같은 장비 계열의 상위 버전도 같은 원칙으로 기본형을 직접
편집합니다. CSS 테두리 변화만으로 상위 이미지를 대신하지 않습니다.

## 생성 원본과 저장소 자산

built-in `image_gen`이 만든 1254×1254 작업 원본은 다음 Git 외부 폴더에
보존합니다.

```txt
C:\Users\HOME\.codex\generated_images\019f64cb-07a2-7bb3-81e9-e66fdced3b76
```

게임이 실제 사용하는 파일은 위 프로젝트 경로의 256×256 파생 PNG뿐입니다.
생성 원본 폴더, 합본 검토 이미지와 중간 후보는 Git에 포함하지 않습니다.

## 검증 범위

`tools/smoke/game/smoke_v369_item_and_skill_icons.js`는 다음을 fail-closed로
확인합니다.

- 21개 파일의 PNG signature와 정확한 256×256 크기
- 초보자 무기 1개, 강화권 10개, 검신 스킬 10개의 누락 없는 파일 연결
- 강화권 이름과 `Q → W → E → R → T → F → D → SQ → SW → M` 경로의 1:1 대응
- 기존 저장 데이터의 초보자 무기·강화권도 새 로컬 이미지로 정규화되는지 확인
- 검신 슬롯별 새 이미지와 색 계열, 이미지 안 키 문자·숫자 미사용
- legacy 정적 배포 산출물에 21개 PNG가 포함되는지 확인
- 실제 `http://127.0.0.1:5500/index.html`에서 스킬창, 가방과 아이템 상세의
  정사각형 렌더링·CSS 테두리·브라우저 오류 확인

검증 결과 v369 전용 smoke, seed 추출 smoke, 관련 기존 아이콘·런타임·정적 배포
smoke와 core smoke가 통과했습니다. 실제 Chrome 게임 화면의 기본 스킬 8개와
별도 21개 검수 화면은 모두 256×256 원본을 68×68 정사각형으로 로드했고 실패한
이미지와 브라우저 오류는 0건이었습니다. 정적 generated seed 4개는 현재 로컬
이미지 URL로 재추출했지만 실제 DB write·seed 실행·migration은 하지 않았습니다.
필요한 새 extension, 권한과 설치는 없으며 서버 재시작과 Render deploy도
필요하지 않습니다.
