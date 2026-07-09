이전 채팅에서 이어서 할게. 첨부한 zip은 v204 `backend admin shared utils service split` 완료본이야.

중요한 진행 원칙:
- 나는 코딩/터미널/경로에 익숙하지 않으니까, 명령어를 줄 때는 반드시 실행 위치를 먼저 적어줘.
- git 명령은 가능하면 `git status && git add . && git commit ... && git push`처럼 한 번에 복사 가능한 한 코드 블록으로 줘.
- 오류가 나면 그때 고치면 되니까, 네 판단으로 과감하게 다음 단계 진행해도 돼.
- route/schema/API 응답/DB/env는 꼭 필요한 경우가 아니면 변경하지 마.

현재 완료:
- v198 backend admin service split contract
- v199.1 overview/save snapshots service split + hotfix
- v200 master catalog/detail/relations service split
- v201 create lifecycle service split
- v202 change logs/detail/rollback service split
- v203 edit draft preview/apply service split
- v204 shared utils service split

v204 확인값:
```js
checkAdminReadOnlyPageReady().version
// v204.backend-admin-shared-utils-service-split

checkAdminReadOnlyPageReady().backendSharedUtilsServiceSplitReady
// true

getAdminBackendServiceSplitContractReadiness().splitStatus
// shared-utils-extracted-v204
```

다음 추천:
1. v205 backend admin config split
2. `backend/app/services/admin/admin_config.py` 생성
3. `AdminService` facade에 남은 대형 상수/설정 묶음 이동
4. route/schema/API/DB/env 변경 없이 진행
5. v205 전용 smoke 추가
6. core smoke/compileall 검증
