# 🧱 TECH STACK – Python 라이브러리 프로젝트

이 프로젝트는 Python 기반 라이브러리 개발을 위한 현대적인 기술 스택을 따릅니다.

---

## 🐍 Python & 환경 관리

- Python `>=3.11`
- [uv](https://github.com/astral-sh/uv) – 가상환경 생성 및 패키지 설치
- `uv.lock` – 의존성 잠금 파일로 재현 가능한 빌드 보장

---

## 🛠 프로젝트 관리 & 빌드

- [hatch](https://hatch.pypa.io/) – 프로젝트 생성 및 빌드 시스템
- `pyproject.toml` – 표준 구성 파일
- [build](https://pypa-build.readthedocs.io/) – 패키지 빌드
- [twine](https://twine.readthedocs.io/) – 패키지 배포 (GitHub 또는 PyPI)

---

## ✅ 테스트 및 커버리지

- [pytest](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)

---

## 🧹 정적 분석 및 코드 품질

- [ruff](https://docs.astral.sh/ruff/) – 린트 & 포맷팅
- `ruff.toml` – 세밀한 린트 규칙 설정
- [mypy](https://mypy-lang.org/) – 타입 검사
- [pre-commit](https://pre-commit.com/) – 커밋 훅으로 ruff & mypy 실행

---

## 🧾 문서화

- [Sphinx](https://www.sphinx-doc.org/)
- 확장: `autodoc`, `napoleon`
- 테마: `sphinx-rtd-theme`
- `README.md` – 프로젝트 개요
- `USAGE.md` – 상세 사용법 가이드

---

## 🚀 CI/CD 및 배포

- [GitHub Actions](https://github.com/features/actions)
  - `ci.yml` – 다중 Python 버전 테스트 (3.11, 3.12, 3.13)
  - `release.yml` – 자동 PyPI 배포
- [Codecov](https://codecov.io/) – 테스트 커버리지 시각화
- 배포 방식: GitHub Release 또는 PyPI

---

## ⚡ 개발 자동화

- `Makefile` – 개발 명령어 자동화 (test, lint, build 등)
- 커버리지 리포트 – HTML 형태로 테스트 커버리지 시각화

---

## 📦 도구 요약

```
uv               # 빠른 설치 및 가상환경
uv.lock          # 의존성 잠금
hatch            # 프로젝트 관리 & 빌드
pytest           # 테스트
pytest-cov       # 테스트 커버리지
ruff             # 코드 린트 및 포맷팅
ruff.toml        # 린트 규칙 설정
mypy             # 타입 검사
pre-commit       # Git 훅
sphinx           # 문서화
build            # 패키지 빌드
twine            # PyPI 배포
Makefile         # 개발 자동화
```
