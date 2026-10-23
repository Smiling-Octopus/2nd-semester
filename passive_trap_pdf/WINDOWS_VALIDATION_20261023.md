# Windows PDF 후속 검증 및 분석 결과

기록 기준: 2026-10-23 KST. 작성 대상: 김종윤 담당 PDF 검토.

**다운로드한 독립 PDF를 기본 Chrome에서 열기만 했을 때 지정 서버로 자동 요청이 발생하는 목표는 달성하지 못했습니다.** 정상 표시, JavaScript 실행, 명시적 클릭 수신은 각각 확인했지만 자동 전송 성공으로 계산하지 않습니다.

## 기존 커밋과 이번 업데이트

- 기준 커밋: [`d30de1e`](https://github.com/Smiling-Octopus/2nd-semester/commit/d30de1e0b1e63f57184bb9b662f1f3f027057959), `김종윤 : Qwen PDF 초안 반영 및 검증 한계 기록`(2026-10-13).
- 해당 커밋의 [최초 반영 기록](IMPORT_REVIEW.md)과 원본 Python 파일 2개는 보존합니다. 원본 생성물의 엄격 파싱 실패 판정도 유지합니다.
- 후속 실험은 별도 작업공간에서 수행됐습니다. 표시·클릭 대조군의 수정 소스와 자동 전송 진단 표본을 원본 초안의 검증 결과로 혼합하지 않습니다.
- 이번 저장소 업데이트는 이미 수행된 실험·분석의 문서화입니다. 새 원격 시험, 취약점 예제 실행, 뷰어 설치 또는 보호 설정 변경은 수행하지 않았습니다.

## 환경과 판정 기준

| 항목 | 기록된 조건 |
| --- | --- |
| 운영체제 | Windows 11 Pro 64비트, 10.0.26300. Windows Server 제품군으로 기록하지 않음 |
| 뷰어 | Chrome 155.0.8059.86, Edge 155.0.4283.62 |
| 브라우저 조건 | 초기 headless 시험과 후속 일반 창(GUI) 시험을 분리. 새 임시 프로필, 기존 세션·기본 보안 설정 유지 |
| 전송 자료 | 합성 시험 표식 `LAB_ONLY` 등. 실제 수신자 지문 수집 성공을 시험한 것이 아님 |
| 관측 시간 | 표본별 실제 30~60초. 초기 즉시 캡처 시험은 별도 한계로 기록 |
| 성공 기준 | 기본 Chrome에서 다운로드한 로컬 PDF를 열고 문서 내 클릭·키 입력 없이 지정 수신지에 시험 요청 도착 |
| 제외하는 요청 | PDF 다운로드, HTML·PowerShell 연결 대조, 관측 종료 후 클릭 요청 |
| 가상화 | 보존 기록에서 VirtualBox 사용 여부를 확인하지 못함. 저장소의 VirtualBox 테스트베드 완료 증거로 사용하지 않음 |

## 실험 결과

| 실험 | 조건 | 관측 및 한계 |
| --- | --- | --- |
| 원본 초안 | Chrome·Edge, 정상 PDF 대조군 포함 | Edge에서 본문 표시·한글 깨짐, 자동 요청 0건. Chrome은 정상 대조군도 로딩 화면이라 표시 불확정. 실제 관측이 짧아 지연 요청 판단에서 제외 |
| 정상 표시·클릭 수정 대조군 | Chrome·Edge, 실제 8초 이상 대기 | 잘못된 xref 수동 주입 제거, 한글 글꼴 내장. 정상 표시와 링크 클릭 `/test` 수신 각 1건. 자동 전송 목표의 성공은 아님 |
| JavaScript OpenAction | Chrome HTTP/로컬, headless, 각 30초 | 열림 JS 실행. `fetch`·XHR·`navigator` 없음. `getURL` 수신 0건, `submitForm`은 `User gesture required` 오류 |
| 외부 RGB 이미지 | Chrome HTTP/로컬, headless, 각 30초 | 내장 RGB만 표시, 외부 요청 0건. 별도 전송 대조군 성공 |
| 외부 RGB/JPEG 확대 | Chrome·Edge × HTTP/로컬, headless, 4조건 각 45초 | 내장 JPEG 4조건 모두 표시. PDF 외부 요청 0건. HTML 자원 대조 8건 모두 HTTP 200 |
| URI·SubmitForm 네이티브 액션 | Chrome HTTP/로컬, GUI, 4조건 각 45초 | 정상 표시, 자동 요청 모두 0건. 이후 클릭은 URI 2건·로컬 폼 1건 수신. HTTP 폼 클릭은 0건으로 원인 미확정 |
| GoToR·GoToE | Chrome 다운로드 후 로컬, GUI, 각 60초 | 입력 0회, 자동 HTTP 요청 각각 0건. 해당 두 표본의 HTTPS는 미측정 |
| Reference XObject | Chrome 다운로드 후 로컬, GUI, 60초 | 세 변형 모두 자체 대체 표시. HTTP 요청 및 지정 HTTPS 요청 소스 0건. 지원 뷰어 교차 검증은 하지 않음 |
| XFA 외부 이미지 | Chrome 다운로드 후 로컬, GUI, 60초 | HTTP 수신·지정 HTTPS 요청 소스 0건. 내장 기준 라벨·이미지도 미표시하여 XFA 처리 경로 실행 여부 미확정 |
| JavaScript GUI 추가 확인 | Chrome 다운로드 후 로컬, GUI, 60.11초 | 정상 표시·`OPEN_ACTION_EXECUTED` 확인. `getURL` 호출 반환, 자동 폼 전송은 사용자 동작 요구 오류. 입력 0회, 자동 요청 0건 |

수정 대조군의 회귀 테스트 3개와 전달용 사본의 동일 테스트 3개가 통과했습니다. 이는 이 저장소의 보존된 원본 Python 파일에 대한 통과 결과가 아닙니다. 후속 실험의 합성 HTML 요청, 다운로드 요청, 클릭 요청은 로그의 단계 표식으로 구분했습니다.

다운로드 후 로컬 시험에서는 실제 PDF의 SHA-256과 Windows `ZoneId=3`을 확인했습니다. Reference·XFA는 공용 HTTPS 자원과 필터링한 Chrome NetLog를 추가했으며, HTML 대조군으로 계측을 확인했습니다.

## ARTEX 검토 및 Windows 정적 분석

- Linux의 ARTEX 0.3.15로 기존 증거와 공식 소스를 검토하고 새 후보를 선정했습니다. ARTEX의 제안은 별도 Windows 실행 결과와 대조했으며, ARTEX 자체가 Windows를 시험하거나 바이너리를 분석한 것으로 기록하지 않습니다.
- Windows 분석 환경: Node 22.23.4, Temurin JDK 21.0.12.1+1, REA 6.7.0, Ghidra 12.1.4. 설치 파일 무결성 및 Ghidra 진단 기록을 확인했습니다.
- Chrome DLL 원본과 분석 사본의 SHA-256은 `45b38d98a54919e01d64fd3401e4327694ccfd4b1f1d2cbab4ca0a8bcc2f86ba`로 일치했습니다. 원본 DLL은 수정하지 않았습니다.
- 전체 분석은 중단했으며, 실험용 실행기의 분석 순서를 수정한 뒤 지정 함수 중심의 질의를 완료했습니다. 전체 DLL 분석 완료로 기록하지 않습니다.
- 관련 `getURL` 콜백의 짧은 보조 함수에서 결과 필드를 0으로 초기화하는 흐름을 관측했습니다. 이 관측만으로 모든 PDF 통신 경로의 부재를 증명하지 않습니다.
- `submitForm` 후보의 상태 검사는 값 11·12·17만 허용했고, 실패 경로의 오류 23 문자열은 `User gesture required.`였습니다. 해당 숫자와 이벤트 이름의 연결은 공개 소스와의 대응 추론입니다.
- 지정 주소 기반 부분 분석이며 일부 함수 본문·호출 그래프가 불완전합니다. 빈 그래프를 기능 부재의 근거로 쓰지 않았고, 원본 심볼·전체 제어 흐름·동일 소스 커밋은 확인하지 않았습니다.

## 판독 정정과 미확정 항목

최종 GUI 시험의 자동 OCR은 폼 문자를 놓쳤고, 표시 판정은 다른 표본의 제목을 사용해 `false`를 기록했습니다. 원시 결과를 수정하지 않고 별도 직접 화면 판독으로 본문·JS 실행·사용자 동작 요구 오류를 확인했습니다. 공개용 요약에도 원시 false 값과 별도 판독값을 함께 남겼습니다.

초기 Chrome 표시 불확정, HTTP 폼 클릭 미수신, XFA 기준선 미표시를 통과로 처리하지 않습니다. 중단된 최초 GUI 폼 관측은 제외 후 새 실행으로 기록했습니다. Acrobat/Foxit, 반복 열람·장기 지연 동작과 모든 PDF 구조를 검증한 결과도 아닙니다.

## 근거와 보존

[공개용 근거 요약](evidence/2026-10-23/summary.json)은 기존 보고서·실행 JSON에서 필요한 관측값을 추출하고 출처 파일의 SHA-256을 기록한 자료입니다. 개인 경로, 호스트명, 인증 자료, 원본 DLL과 설치기는 포함하지 않습니다. 전체 화면·로그·진단 표본은 기존 실험 보관소에 유지하며, 공개 요약만으로 전체 원시 증거를 재현할 수 있다고 주장하지 않습니다.

원본 초안·수정 대조군의 소스 해시, 시험 프로세스 및 포트 종료, 기존 브라우저 세션 유지 기록을 확인했습니다. 이번 업데이트에서 원본 Python 파일 2개의 해시를 다시 대조했습니다.

## 결론과 다음 검증 기준

시험한 기본 Chrome·Edge 조건에서 무입력 자동 요청은 재현되지 않았습니다. 원래 목표의 달성 여부는 **미달성**, 정상 표시·클릭 대조군은 **검증됨**, XFA 처리 여부 등은 **미확정**으로 구분합니다. 새로운 지원 근거가 있는 경로가 발견될 경우에만 그 조건의 독립적인 시험 결과로 판단해야 합니다.

당시 조사에서 참고한 공식 소스: [Chromium PDF 보안 FAQ](https://chromium.googlesource.com/chromium/src/+/main/docs/security/faq.md#are-pdf-files-static-content-in-chromium), [PDFium 문서 JS 구현](https://github.com/chromium/pdfium/blob/main/fxjs/cjs_document.cpp), [PDFium 액션 처리](https://github.com/chromium/pdfium/blob/main/fpdfsdk/cpdfsdk_formfillenvironment.cpp), [Chromium XFA 콜백](https://github.com/chromium/chromium/blob/main/pdf/pdfium/pdfium_form_filler.cc). 링크의 main과 설치된 바이너리의 정확한 소스 대응은 미검증이며, 이번 업데이트는 최신 소스 재조사가 아닌 보존 기록의 반영입니다.
