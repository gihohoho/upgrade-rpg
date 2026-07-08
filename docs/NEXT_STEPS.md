# Next Steps

## 다음 추천: v169 create-delete restore preview 설계 또는 create apply 도메인 확장

안전하게 가려면 삭제된 create row를 바로 복원하지 말고, 먼저 `create_delete` 이력 기반 restore preview를 설계한다.

조금 더 기능을 넓히려면 `fieldZones`처럼 relation 의존도가 낮은 도메인을 create apply allow-list에 추가할 수 있다.

주의: `itemTemplates`, `skills`, `dropTables`는 관계/런타임 영향이 커서 생성 apply를 열기 전에 더 긴 검증이 필요하다.
