# Git Workflow

이 프로젝트는 이제 파일 수가 많아졌기 때문에 Git으로 버전을 관리합니다.

## 기본 흐름

```bash
git status
git add .
git commit -m "작업 내용"
git push
```

## 새 ZIP을 받은 뒤 추천 흐름

1. 기존 프로젝트를 백업합니다.
2. 새 ZIP을 풀고 파일을 적용합니다.
3. 실행 확인 후 커밋합니다.

예시:

```bash
git status
git add .
git commit -m "v076 dev environment setup"
git push
```

## 커밋 메시지 예시

```txt
v075 backend foundation draft
v076 dev environment setup
fix damage text position
refactor boss data split
```

## 절대 올리지 말아야 할 것

```txt
backend/.env
backend/.venv/
.venv/
__pycache__/
*.zip
```

이번 v076에서 `.gitignore`를 추가해 위 파일들이 올라가지 않도록 했습니다.
