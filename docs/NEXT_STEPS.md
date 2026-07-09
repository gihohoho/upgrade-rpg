# Next Steps

## 현재 완료: v197 admin settings/helpers split

`API base URL`, `admin write dev key`, `현재 관리자 URL`, `게임 URL`, `주소 복사` helper를 `src/api/admin/admin-settings-helpers.js`로 분리했습니다.

## 다음 추천: v198 admin entry final cleanup 또는 backend admin service split 준비

관리자 프론트의 큰 JS 분리는 대부분 끝났습니다. 다음은 코드 상태를 보고 아래 둘 중 하나를 선택하면 좋습니다.

1. 프론트 entry 최종 정리
   - `admin-page-readonly.js`에 남은 legacy marker / wrapper / readiness aggregation 정리
   - 기존 window 함수명 유지
   - 전용 smoke 추가

2. 백엔드 admin service split 준비
   - `backend/app/services/admin_service.py` 또는 관련 admin 파일이 커졌는지 확인
   - 바로 분리하지 않고 service split contract 문서/smoke를 먼저 추가
   - API route/schema 변경 없이 내부 구조만 준비

## 주의

다음 단계에서도 DB schema/env 변경은 최대한 피하고, 기존 게임 정상 작동 상태를 유지합니다.
