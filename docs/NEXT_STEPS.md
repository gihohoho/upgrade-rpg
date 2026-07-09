# Next Steps

## 현재 완료: v192 admin master catalog/detail split

`master catalog/detail` 구현을 `src/api/admin/admin-master-catalog.js`로 1차 분리했습니다.

## 다음 추천: v193 admin overview/snapshots split

다음은 DB 쓰기와 직접 관련이 적은 overview/snapshot 계열을 실제 분리하는 것이 좋습니다.

추천 후보 파일:

```txt
src/api/admin/admin-overview-snapshots.js
```

추천 범위:

1. overview cards 렌더링
2. save snapshot 필터 read/reset/describe
3. save snapshot table 렌더링
4. snapshot 관련 readiness
5. 기존 window export wrapper 유지
6. 전용 smoke 추가

이 단계가 끝나면 `admin-page-readonly.js`는 bootstrap/event binding/window wrapper에 더 가까워집니다.
