# Master Data Nested Asset Cleanup

`v084`는 `v083`에서 발견된 남은 asset 문제를 보정합니다.

## 문제

`v083`에서는 `/api/v1/game/master-data` 기본 응답에서 아래 최상위 필드를 `null`로 바꿨습니다.

```txt
characters.imageUrl
skills.iconUrl
itemTemplates.iconUrl
bosses.imageUrl
```

하지만 seed 데이터에는 `options`, `conditions`, `rules`, `raw` 같은 중첩 JSON 안에도 아래와 같은 긴 data URL이 남아 있을 수 있습니다.

```txt
data:image/svg+xml;charset=UTF-8,%3Csvg...
```

그래서 기본 응답 검사에서 여전히 백신 오탐 가능성이 있는 긴 문자열이 감지될 수 있었습니다.

## 수정

기본 응답에서는 중첩 JSON 안의 inline image data URL도 재귀적으로 `null`로 바꿉니다.

```txt
includeAssets=false  → 모든 중첩 data:image... 문자열 null 처리
includeAssets=true   → 모든 중첩 data:image... 문자열 그대로 포함
```

## 확인

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/check_master_data_api.py
```

정상이면 다음처럼 출력됩니다.

```txt
master-data API check passed
```

asset 포함 응답도 확인하려면:

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/check_master_data_api.py --include-assets
```
