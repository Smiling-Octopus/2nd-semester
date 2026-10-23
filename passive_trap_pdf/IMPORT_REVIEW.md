# ZIP 반영 및 검토 기록

이 문서는 2026-10-13 커밋 `d30de1e0b1e63f57184bb9b662f1f3f027057959`의 최초 반영 기록입니다. 아래 당시 결과는 보존하며, 2026-10-23의 후속 실험은 문서 마지막의 연결 자료에서 별도로 확인합니다.

## 출처와 반영 방식

- 입력: `qwen-next-workspace.zip`
- 입력 ZIP SHA-256: `baa4cfdcabc45a9d449b271544b2958f9ee3e3a45036fa6f002f0423d296aaa8`
- 대상 브랜치: `feature/kjy/benign_pdf_js_verification`
- 반영 기준 커밋: `901a17e5af7e16ce6e4aba482efbc2215eda222f`
- ZIP 내부 `qwen-next-workspace/passive_trap_pdf/`의 Python 파일만 원문 그대로 반영했습니다.
- 원본 README와 TEST_CHECKLIST는 코드와 맞지 않는 성공 단정 및 제3자 추적·위장 안내 대신, 검증된 사실과 테스트베드 한계를 설명하는 문서로 대체했습니다.
- 루트의 중복 `server.py`, `trap_pdf_generator.py`는 각각 하위 폴더 원본과 바이트가 같아 중복 반영하지 않았습니다.
- `.qwen-backups/`, `uploads/`, `verification/check.csv`는 편집 백업·입력 자료·샘플 CSV이므로 제외했습니다. 해당 CSV는 PDF 검증 결과로 사용하지 않았습니다.
- 기존 `benign_pdf_js/`, 취약점 예제 및 `example.pdf`는 수정하지 않았습니다. 취약점 예제는 실행하지 않았습니다.

## 원본 소스 SHA-256

```text
127d50f4301bda92c3027928fbf6837aeed8714a612e2c97fc467f4a16450303  server.py
d8a3ae6f8c72c8642133ba43ebd9f2dcc5087740d3b5fe2b5a2c2c5675abdb26  trap_pdf_generator.py
```

## 실행 확인

로컬 격리 venv: Python 3.14, Flask 3.1.3, ReportLab 5.0.1, Pillow 12.3.0, pypdf 6.20.0. 설치 과정과 분리하여 검토 프로세스에서는 소켓 생성/연결을 거부했습니다. Flask 서버를 리슨하지 않고 `app.test_client()`만 사용했습니다. 생성물과 합성 로그는 Git 밖 임시 폴더에서만 만들었습니다.

- 구문 검사: 두 파일 모두 `ast.parse` 통과.
- `/track?case=LOCAL_TEST`, `/pixel?case=LOCAL_TEST`: 두 경로 모두 HTTP 200, `Content-Type: image/gif`, `Cache-Control: no-store`.
- 합성 로그: 2줄. IP는 테스트용 `127.0.0.1`, User-Agent는 `offline-test-client`.
- GIF: Pillow `Image.open(...).load()` 통과, 크기 1×1.
- `make_1x1_gif()` 다음 `build_pdf()` 실행: `trap.pdf` 파일 생성.
- `PdfReader('trap.pdf', strict=True)`: **FAIL**, `PdfReadError: Trailer cannot be read: '/Type'`.
- 기존 회귀 검사: `python -m unittest -v test_artifacts.py` 5개 통과; `node test_js.cjs`의 모의 실행 및 금지 연산 검사 통과; `sha256sum -c SHA256SUMS` 4개 일치.

위 결과는 수집 서버의 프로세스 내 응답과 파일 구조 검사에 한정됩니다. 실제 Acrobat/Foxit/Chrome/Edge 동작, 외부 전송, 반복 열람 관측은 검증하지 않았습니다.

## 소스에서 발견한 문제 — 이번 반영에서는 수정하지 않음

1. `pixel_url`은 실제 PDF 외부 리소스로 연결되지 않습니다. 로컬 GIF 삽입만으로 열람 시 HTTP 요청이 생기지 않습니다.
2. PDF 바이트 중간에 내용을 삽입한 후 기존 xref 오프셋을 재사용하며, `startxref` 값은 새 xref 테이블이 아닌 추가 객체 시작 위치로 설정됩니다. 페이지 액션 값도 별도 구조 검토가 필요합니다. 실제 엄격 파싱 실패와 구분하여 기록한 정적 관찰입니다.
3. 코드 설명과 달리 PDF Catalog의 `/OpenAction`을 설정하는 방식이 아니라 페이지 `/AA`를 추가하려고 합니다. 문자열 검색만으로 정상 이벤트 연결을 판정할 수 없습니다.
4. `getURL`의 호출이 뷰어별 무경고 전송을 보장하지 않습니다. 예외를 삼키므로 무반응도 성공이 아닙니다.
5. `X-Forwarded-For` 신뢰, 제한 없는 요청 로그, `0.0.0.0` 기본 바인딩은 운영 보안 검토가 필요합니다.

**판정: 원본 초안 반영 완료와 작동 검증 완료는 별개입니다. 현재 코드는 `UNVERIFIED_DRAFT`이며 운영·실전 사용 가능으로 판정하지 않습니다.**

## 후속 기록 — 2026-10-23

- [Windows 후속 실험 및 분석 결과](WINDOWS_VALIDATION_20261023.md)에 Chrome·Edge 실제 표시, 클릭 수신, 자동 전송 후보 시험과 REA·Ghidra 정적 분석을 추가했습니다.
- 별도 작업공간의 정상 표시·클릭 대조군과 이 저장소에 보존한 원본 초안을 구분합니다. 이 폴더의 두 Python 파일은 위 원본 SHA-256을 유지합니다.
- 후속 결과에서도 다운로드한 로컬 PDF를 기본 Chrome에서 열기만 해 자동 전송하는 목표는 달성하지 못했습니다. 클릭 성공, HTML 대조군 요청, PDF 다운로드를 자동 전송 성공으로 계산하지 않습니다.
- 공개용 관측값과 근거 자료 해시는 [근거 요약](evidence/2026-10-23/summary.json), 주차별 3줄 정리는 [진행 요약](WEEKLY_PROGRESS.md)에 있습니다.
