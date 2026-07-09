# Next Steps — after v216

다음 추천 단계는 **v217 admin route legacy smoke marker cleanup**입니다.

1. `admin.py` 하단의 legacy static-smoke marker 주석을 더 짧게 정리
2. 오래된 smoke가 실제 route module 파일을 보도록 조금씩 조정
3. `admin.py`를 최종적으로 include facade + 최소 주석만 남기기
4. route path/schema/API 응답 구조는 그대로 유지
5. v217 전용 smoke 추가

그 다음 후보는 admin route module별 README 또는 route registry 문서화입니다.
