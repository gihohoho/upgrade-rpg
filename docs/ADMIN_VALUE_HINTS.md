# Admin Value Hints

v121 단계에서는 관리자 페이지에서 필드명 설명뿐 아니라, 실제 값이 무엇을 뜻하는지도 짧게 표시한다.

## 핵심 변경

v120에서 `grade`를 일반적인 희귀도 예시인 `normal`, `rare`, `epic`, `unique`, `legendary`처럼 설명했지만, 현재 프로젝트 DB의 `itemTemplates.grade`는 그렇게 쓰이지 않는다.

현재 DB seed 기준:

```txt
itemTemplates.grade = 기존 JS item.tier 값을 문자열/숫자 형태로 옮긴 값
```

즉 `grade=1`, `grade=7`, `grade=12` 같은 값은 희귀도 이름이 아니라 아이템 진행 구간/티어 숫자다.

## grade 해석

`grade`는 현재 다음처럼 이해한다.

```txt
grade 1  = 1티어 / 초반 구간
grade 7  = 7티어 / 중간 이후 구간
grade 12 = 12티어 / 상위 구간
```

이 값은 아이템이 어느 보스/장비 성장 구간에 속하는지, 드랍 단계와 장비 진행도를 맞출 때 참고하는 값이다.

희귀도 이름이 필요해지면 `grade`를 억지로 바꾸지 말고, 나중에 별도 필드로 분리하는 편이 안전하다.

예:

```txt
grade = 12
rarity = legendary
```

## 화면 표시

관리자 페이지에서 아래 위치에 값 해석 힌트가 붙는다.

- 마스터 데이터 카탈로그 표
- 마스터 데이터 상세 기본 필드
- 관리자 편집 초안 입력칸

예:

```txt
12
tier 12 — 현재 값 12은 희귀도명이 아니라 원본 아이템 tier 12입니다.
```

## enhance group code 해석

`enhance_group_code`는 아이템을 강화 규칙 묶음에 연결하는 코드다.

현재 자동 추론되는 대표 값:

```txt
normal_equipment  = 일반/심연/특수/avatar 계열 장비 강화 규칙
talisman_emblem   = 탈리스만/빛나는 휘장 강화 규칙
```

## admin note 해석

`admin_note`는 게임 화면에 보이지 않는 내부 메모다.

값이 비어 있으면 “관리자 메모 없음”, 값이 있으면 “관리자 메모 있음” 힌트가 표시된다.

## Console helper

```js
// 위치: 브라우저 개발자도구 Console
getAdminFieldValueHint("grade", 12);
getAdminFieldValueHint("enhanceGroupCode", "normal_equipment");
getAdminFieldHelp("grade");
```

## 안전장치

이번 단계는 관리자 화면 설명/값 해석만 추가한다.

- DB 수정 없음
- localStorage 수정 없음
- 게임 런타임 수정 없음
- 쓰기 API 추가 없음
- 저장 버튼은 계속 잠김

DB reset/seed는 필요 없습니다.
