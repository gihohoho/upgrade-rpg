# Master Data Asset Policy

`v083`부터 `/api/v1/game/master-data`는 기본 응답에서 긴 이미지 문자열을 제외합니다.

## 이유

현재 seed 데이터에는 아래처럼 긴 SVG data URL이 들어 있습니다.

```txt
data:image/svg+xml;charset=UTF-8,%3Csvg...
```

이 문자열은 실제 바이러스라기보다는 로컬 개발 API 응답 안에 포함된 긴 SVG 문자열입니다. 하지만 일부 백신/브라우저 보안 기능은 JSON 응답 안의 긴 SVG data URL을 의심스럽게 보고 경고를 띄울 수 있습니다.

## 기본 응답

위치: **브라우저 주소창**

```txt
http://127.0.0.1:8000/api/v1/game/master-data
```

기본 응답에서는 아래 필드가 `null`로 내려갑니다.

```txt
characters.imageUrl
skills.iconUrl
itemTemplates.iconUrl
bosses.imageUrl
```

대신 실제 이미지 데이터가 있는지 알 수 있도록 아래 값은 유지합니다.

```txt
hasImage
hasIcon
assetPolicy
```

## 이미지 문자열까지 포함해서 확인하기

위치: **브라우저 주소창**

```txt
http://127.0.0.1:8000/api/v1/game/master-data?includeAssets=true
```

이렇게 요청하면 기존처럼 긴 `imageUrl`, `iconUrl` data URL까지 포함됩니다.

## 터미널 확인

기본 경량 응답 확인:

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/check_master_data_api.py
```

이미지 문자열 포함 응답 확인:

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/check_master_data_api.py --include-assets
```

## 이후 방향

나중에 Vue/Vite 프론트엔드로 전환할 때는 긴 data URL을 API로 직접 내려주는 방식보다 아래 방식이 더 안전합니다.

```txt
DB/API: iconKey, imageKey, assetPath 같은 짧은 참조값 제공
Frontend: public/assets 또는 CDN/static 경로에서 이미지 로드
```

이번 v083은 그 전 단계로, 기존 seed 구조를 크게 바꾸지 않으면서 백신 오탐과 응답 크기 문제를 줄이는 안전한 조치입니다.
