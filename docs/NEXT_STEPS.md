# Next Steps — after v246

다음 추천 단계는 **v247 backend admin preview side-effect static contract**입니다.

## 목표

1. preview service 메서드에서 `commit()` 호출 금지
2. preview service 메서드에서 `flush()` 호출 금지
3. preview service 메서드에서 `add()`·`delete()` 호출 금지
4. apply 메서드가 mutation boundary인지 정적 확인
5. rollback/예외 처리용 호출은 메서드별로 구분
6. 실제 DB 호출 없이 AST/static contract로 검증

## 작업 원칙

- 실제 DB 쓰기 금지
- 기존 write guard 유지
- API 주소/응답 body/schema 변경 금지
- backend/frontend parity smoke 필수
- FastAPI/Starlette/Pydantic 결과는 실행 관찰 후 계약화
