# sb-libs-py 사용법 (USAGE)

## 📁 패키지 구조

src/sb_libs/
├── __init__.py                    # 메인 패키지 (testing 서브패키지 포함)
└── testing/                       # 테스트 유틸리티 패키지
    ├── __init__.py               # 모든 도구 export
    ├── __main__.py               # CLI 인터페이스
    ├── detect_unittest_usage.py  # unittest 사용 감지
    ├── naming_validator.py  # 테스트 명명 규칙 검증
    └── unittest_to_pytest_migrator.py  # unittest→pytest 마이그레이션

---

## 🔧 주요 기능 및 개선사항

- **모듈 접근성**: sb_libs.testing 네임스페이스로 모든 도구 사용 가능
- **CLI 인터페이스**: 통합 및 개별 실행 지원
- **패키지화**: pip install 후 즉시 활용 가능
- **테스트 파일 포함**: 예제 및 검증 코드 제공

---

## 1. 라이브러리로 사용하기

```python
from sb_libs.testing import NamingValidator, UnittestToPytestMigrator
```

---

## 2. CLI 사용법

### (1) 통합 CLI

```bash
python -m sb_libs.testing detect-unittest file1.py file2.py
python -m sb_libs.testing validate-naming tests/ --detailed
python -m sb_libs.testing migrate-unittest tests/ --dry-run
```

### (2) 개별 도구 실행

```bash
python -m sb_libs.testing.detect_unittest_usage file.py
python -m sb_libs.testing.naming_validator tests/
python -m sb_libs.testing.unittest_to_pytest_migrator tests/
```

---

## 3. 패키지화 및 활용

- 모든 도구는 `sb_libs.testing` 네임스페이스로 접근
- 명확한 패키지 구조와 문서화
- 테스트 파일 포함
- 다른 프로젝트에서 pip install sb-libs-py 후 바로 사용 가능

---

## 문의 및 기여

- 개선 제안, 버그 제보, PR 환영합니다!
