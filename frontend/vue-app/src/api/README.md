# Vue API 계층

화면은 store를 통해 아래 client를 호출합니다. 응답 타입은 `contracts.ts`, 실제 API 계약은 [API Response Contract](../../../../docs/contracts/API_RESPONSE_CONTRACT.md)를 따릅니다.

| 영역 | client | 역할 |
|---|---|---|
| 로그인·이메일 | `authApi.ts` | 계정 인증과 이메일 요청 |
| 캐릭터 | `accountApi.ts` | 계정별 슬롯 조회·생성·삭제, master-data 조회 |
| 게임 저장 | `gameApi.ts` | 선택 캐릭터 load와 단일 직렬 queue의 save |
| 관리자 조회 | `adminReadOnlyApi.js` | 도메인·카탈로그·상세·관계·변경 이력 GET |
| 관리자 검토 | `adminPreviewApi.ts` | `dryRun: true`인 Preview POST 5개 |
| 연결 확인 | `healthReadOnlyApi.js` | health GET |

`http.ts`는 typed 요청·timeout·인증 오류를 처리하고, `readOnlyClient.js`는 관리자·health 조회의 GET 제한을 유지합니다. 둘 다 `config.js`의 API 주소를 사용합니다. 게임 조회는 typed client로 통일하여 사용하지 않던 `gameReadOnlyApi.js`를 제거했습니다.

관리자 GET은 store에서 Bearer와 `no-store`를 전달합니다. 상세·관계 wrapper는 `rowId`를 backend query `id`로 바꿉니다. 카탈로그 기본값은 `limit=20`, `page=1`, `sort=id_asc`입니다.

Preview 응답의 `confirmTextRequired`는 화면에만 표시합니다. 관리자 Apply와 dev key header는 연결하지 않았습니다. 계정·캐릭터·게임 저장의 허용된 write와 관리자 Apply를 혼동하지 않습니다.

개발 서버 설치·실행은 [저장소 README](../../../../README.md)를 따릅니다.
