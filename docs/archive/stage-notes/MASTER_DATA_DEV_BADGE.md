# Master Data Dev Badge

v095에서는 브라우저 화면에 백엔드 master-data 적용 상태를 보여주는 개발자용 배지를 추가했고, v096에서는 배지 위치를 bottom HUD 안의 능력치 패널 오른쪽으로 옮겼다. v097에서는 버튼 줄 넘침을 고치고, 숨김/보임을 Console 없이 화면 안에서 처리할 수 있게 했다. v098에서는 토글 버튼을 `hide MD` / `show MD`로 명확히 바꾸고 배지 상단 정가운데 탭처럼 정렬했다.

## 목적

Console을 열지 않아도 현재 게임이 어떤 master-data 모드로 실행 중인지 빠르게 확인하기 위함이다.

표시 예시:

```txt
MASTER DATA  applied
mode: auto   assets: off
counts: B:39 · S:6 · F:40 · I:245
updated: 16:45:10
```

## 기본 표시 정책

배지는 아래 환경에서 기본 표시된다.

```txt
file://
localhost
127.0.0.1
```

운영 배포 환경에서는 기본 표시하지 않는다. 필요하면 Console에서 직접 켤 수 있다.

## 화면 버튼

배지 위쪽에는 작은 토글 버튼이 별도로 표시된다.

| 버튼 | 동작 |
| --- | --- |
| hide MD | 배지를 접는다. 버튼은 배지 상단 정가운데 탭 위치에 남는다. |
| show MD | 접힌 배지를 다시 펼친다. |

배지 내부 버튼은 다음 역할을 가진다.

| 버튼 | 동작 |
| --- | --- |
| refresh | 게임 데이터를 다시 받지 않고, 현재 런타임 상태/개수만 다시 읽어 배지 표시를 갱신한다. |
| auto | auto 모드로 전환 후 새로고침한다. 현재 적용 중이면 초록색 활성 상태로 보인다. |
| static | 기존 JS 데이터 모드로 전환 후 새로고침한다. 현재 적용 중이면 초록색 활성 상태로 보인다. |

`refresh`는 백엔드 API를 다시 호출하는 버튼이 아니다. `enableBackendMasterDataMode()`, `useStaticMasterDataMode()`, API fallback, 자동 부팅 상태 변화 뒤에 배지 표시만 바로 다시 읽고 싶을 때 사용한다. 배지가 5초마다 자동 갱신되므로 평소에는 눌러도 큰 변화가 없어 보일 수 있다. v097부터 `updated` 시간이 표시되어 refresh 동작을 확인할 수 있다.

## Console 함수

화면 버튼을 사용할 수 없는 상황을 대비해 기존 Console 함수도 유지한다.

```js
refreshBackendMasterDataDevBadge();
showBackendMasterDataDevBadge();
hideBackendMasterDataDevBadge();
toggleBackendMasterDataDevBadge();
```

숨김 상태는 `localStorage`에 저장된다. 그래서 새로고침해도 계속 숨겨질 수 있다. 다시 보이게 하려면 화면의 `show MD` 버튼이나 Console의 `showBackendMasterDataDevBadge()`를 사용한다.

## 상태 의미

| state | 의미 |
| --- | --- |
| applied | 백엔드 master-data 적용 성공 |
| backend_auto_waiting_for_page_load | 페이지 로드 후 백엔드 데이터를 적용할 예정 |
| loading | 백엔드 master-data 요청 중 |
| static_js_mode | 기존 JS 데이터 사용 중 |
| failed_fallback_to_static_js | 백엔드 요청 실패 후 기존 JS 데이터로 fallback |

## 배지 위치

배지는 `#bottom-hud` 내부에 붙는다. 위치는 중앙 능력치 패널의 오른쪽이며, 왼쪽 프로필 사진과 반대편이다. `hide MD` / `show MD` 토글은 MASTER DATA 인터페이스 상단 정가운데에 탭처럼 붙어 인터페이스가 접히고 펼쳐지는 느낌으로 동작한다. 작은 화면에서는 오른쪽 위로 이동해 다른 HUD 요소와 겹침을 줄인다.

## 주의

이 배지는 개발 편의 도구이며 게임 데이터 자체를 변경하지 않는다. master-data 적용/전환은 기존 runtime switch와 boot policy가 담당한다.
