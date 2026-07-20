# Backend dependency locks

이 폴더는 운영 이미지와 GitHub Actions 검증 환경의 Python 입력을 고정합니다.

- `*.in`: 사람이 검토하는 직접 의존성 버전
- `*.lock`: CPython 3.11 / Linux amd64용 전체 전이 의존성과 선택 wheel의 SHA-256
- 생성 도구: `tools/generate_backend_linux_dependency_locks.py`

`*.lock`은 직접 수정하지 않습니다. 버전을 바꿀 때는 `*.in`과 `backend/pyproject.toml`을 먼저 검토한 뒤 생성 도구의 `--write`를 사용합니다. 일반 strict 검사에서는 네트워크를 사용하지 않는 `--check`만 실행합니다.

설치는 먼저 고정된 대상 플랫폼 옵션으로 wheel을 다운로드하고, 그 임시 wheel 폴더에서 `--no-index --require-hashes --only-binary=:all:`로 수행합니다. 이 두 단계는 다른 플랫폼 파일이나 source distribution이 섞이는 것을 차단합니다.
