# Next Steps

## 다음 추천: v175 create apply 도메인 제한 확장

관리자 페이지 레이아웃과 접힌 탭 스타일 보강이 끝났으므로, 다음부터 다시 기능 확장을 진행해도 됩니다.

다음 후보는 relation 의존도가 낮은 `fieldZones`를 create apply allow-list에 추가하는 단계입니다.

안전하게 진행하려면 아래 순서가 좋습니다.

1. `fieldZones` create apply만 제한 오픈
2. 생성 row 삭제 dependency guard에 `dropTables.owner_type=field + owner_code` 검사 추가
3. create_delete restore에도 fieldZones 복원 충돌 검증 포함

주의: `itemTemplates`, `skills`, `dropTables`, `dropTableItems`는 게임 런타임 영향과 관계 의존도가 커서 아직 생성 apply를 바로 열지 않는 것이 안전합니다.
