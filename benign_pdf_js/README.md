# 무해한 PDF JavaScript 호환성 테스트

기존 `PDF File Script Code/`와 완전히 분리된 실험입니다. 기존 스크립트나 `example.pdf`를 실행하거나 재사용하지 않습니다.

## 범위

- `control_no_js.pdf`: JavaScript가 없는 대조군. 상태는 `NOT_RUN` 그대로여야 합니다.
- `benign_js_test.pdf`: 문서 JavaScript 실행 시 읽기 전용 필드의 `NOT_RUN`이 `JS_EXECUTED`로 바뀝니다.
- 지원되는 경우 뷰어 종류·버전·variation을 화면 필드에만 표시합니다.
- 팝업, 다운로드, URL 접속, 외부 프로그램 실행, 키 입력 수집, 개인정보 수집, 자동 저장이 없습니다.
- 이 시험은 기존 취약점 코드나 외부 프로그램 연계 기능의 작동을 증명하지 않습니다.

## Windows에서 시험

1. 저장소 정책대로 Windows PC 안의 VirtualBox 테스트 VM에서 수행합니다. 기존 공격용 PDF는 사용하지 않습니다.
2. 처음에는 인터넷을 차단하고, 뷰어 기본 보안 설정을 유지합니다. 결과를 얻기 위해 보호 모드를 끄거나 오래된 취약 뷰어를 설치하지 않습니다.
3. ZIP을 풀고 동일한 뷰어에서 대조군을 먼저 엽니다. `NOT_RUN` 화면을 캡처하고 닫습니다.
4. `benign_js_test.pdf`를 열고 상태와 뷰어 정보 필드를 캡처합니다. 브라우저 미리보기 대신 시험할 뷰어의 **파일 열기** 기능으로 엽니다.
5. 프로그램의 **도움말 → 정보/About** 화면에서 정식 제품명과 전체 버전·빌드, 32/64비트를 별도로 기록합니다. PDF API가 표시하는 버전은 전체 빌드와 다를 수 있습니다.
6. 보안 경고가 뜨면 내용과 기본 설정을 그대로 기록합니다. 우회하거나 신뢰 위치를 추가하지 않습니다.
7. 원본 PDF를 덮어쓰지 말고 `results_template.csv`의 사본과 캡처만 남깁니다. 다시 시험할 때는 ZIP의 원본을 새로 풉니다.

### 결과 해석

- 대조군 `NOT_RUN` + 시험군 `JS_EXECUTED`: 이 파일의 무해한 JavaScript가 해당 환경에서 실행되었다는 증거입니다.
- 시험군도 `NOT_RUN`: **미실행/미관측**입니다. 미지원·설정 차단·표시 갱신 문제를 아직 구분할 수 없습니다. 오류라고 단정하지 않습니다.
- 상태만 변경되고 뷰어 정보가 `UNKNOWN`: 코드 실행과 해당 API 지원 여부를 분리해 기록합니다.
- 캡처와 환경 정보가 없으면 실제 뷰어 PASS로 기록하지 않습니다.
- Node의 모의 객체 테스트와 PDF 정적 검사는 Windows 뷰어 시험을 대체하지 않습니다.

## 재생성 및 개발 검사

Python 3.10+와 Node.js가 필요합니다. 프로젝트 격리 가상환경을 사용하세요.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python generate_pdf.py artifacts
.\.venv\Scripts\python -m unittest -v test_artifacts.py
node test_js.cjs
```

`artifacts` 폴더를 먼저 생성하세요. 재생성 시 파일 바이트/해시는 달라질 수 있으며, 각 시험은 그때 사용한 실제 파일의 SHA-256에 연결해야 합니다.

## 설치 파일 기록 (이번 단계에서는 미확보)

설치 파일은 신뢰할 수 있는 공식 배포처에서 확보하고, Git에는 올리지 않습니다. 별도 보관소에 원본을 보관한 후 `installers_template.csv`에 제품명·버전·출처·확보 시각·SHA-256·서명 검증·경로를 기록합니다. 정식 설치 파일과 웹 부트스트랩 설치기를 구분하고 실제 설치된 버전은 About 화면으로 확인합니다. 설치기 확인 실패나 공식 배포 중단은 미확보로 남깁니다.

```powershell
Get-FileHash .\viewer_installer.exe -Algorithm SHA256
Get-AuthenticodeSignature .\viewer_installer.exe | Select-Object Status,StatusMessage,SignerCertificate
Get-FileHash .\artifacts\benign_js_test.pdf -Algorithm SHA256
```

위 파일명은 기록 방법 예시이며, 실제 설치 파일을 제공했다는 의미가 아닙니다.

## 작성·검증 역할

생성 코드와 내장 JavaScript는 ETRI `qwen-next`의 응답을 검토한 뒤 사용합니다. Pepper가 검증 테스트·한국어 안내·패키징을 담당합니다. 실제 생성/검증 결과는 `verification.json`에 기록하며 Windows 뷰어 시험은 사용자가 캡처를 제공하기 전까지 `NOT_TESTED`입니다.
