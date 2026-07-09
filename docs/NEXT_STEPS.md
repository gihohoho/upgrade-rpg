# Next Steps

## 현재 완료: v191 admin edit draft split

`edit draft` 구현을 `src/api/admin/admin-edit-draft.js`로 1차 분리했습니다.

## 다음 추천: v192 master detail/catalog split contract

다음은 실제 분리보다 먼저 계약 고정이 좋습니다.

추천 범위:

1. master catalog render/pagination 함수 목록 고정
2. master detail open/render 함수 목록 고정
3. master relations render 함수 목록 고정
4. API verify helper 목록 고정
5. DOM target/window export 목록 고정
6. 다음 후보 파일명 고정

후보 파일명:

```txt
src/api/admin/admin-master-catalog.js
src/api/admin/admin-master-detail.js
```

한 번에 둘 다 계약만 고정하는 것은 괜찮고, 실제 분리는 다음 단계에서 하나씩 진행하는 것이 안전합니다.
