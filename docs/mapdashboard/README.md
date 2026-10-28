# MapDashboard 독립 개발

대학 객체지향프로그래밍 팀 프로젝트 「내 서울 공원 길라잡이」의 **화면·이벤트 담당 클래스만** 구현한 독립 개발본입니다. 팀 공유 브랜치는 `feature/map-dashboard`이며 루트 README와 팀 설정 파일은 유지합니다.

실제 Park, ParkManager, DataLoader, 엑셀 읽기/변환/정제는 구현하지 않았습니다. [demo/mocks.py](../../demo/mocks.py)는 테스트 전용입니다.

## 실행

아래 명령은 모두 **저장소 루트** (`run_demo.py`가 있는 폴더)에서 실행합니다. 이 README가 있는 `docs/mapdashboard/`에서 실행하지 마세요.

1. Python 3.10 이상을 설치합니다. pip 패키지 설치는 필요하지 않습니다.
2. Windows에서는 저장소 루트의 [실행.cmd](../../실행.cmd)를 더블클릭합니다. Python Launcher의 `py -3`를 우선 사용하고, 없으면 PATH의 `python`을 사용합니다.
3. 브라우저의 `http://127.0.0.1:8765/demo/index.html`에서 지도를 확인합니다.
4. 종료는 실행 창에서 `Ctrl+C`를 누릅니다.

터미널에서 실행하려면:

```powershell
python run_demo.py
# 브라우저 통합 테스트
python run_demo.py --test
# 8765 포트가 이미 사용 중이면
python run_demo.py --test --port 8766
```

Windows에서 `python`이 설치된 Python을 가리키지 않으면 `py -3 run_demo.py --test`를 사용하거나 Python 설치 시 PATH 설정을 확인하세요. 개인 PC의 특정 런타임이나 캐시에 의존하지 않습니다.

HTML을 파일로 직접 열지 마세요. PyScript가 Python 소스와 설정을 HTTP로 가져오므로 로컬 서버를 사용합니다. 서버는 `127.0.0.1`에만 연결됩니다. 인터넷은 PyScript/Pyodide, Leaflet 및 OpenStreetMap 배경 지도를 불러오는 데 필요합니다. 이 실행 도우미에는 원격 저장소 업로드나 배포 기능이 없습니다.

## 사용법

- 구 드롭다운 변경 시 적용됩니다.
- 면적 입력을 마친 뒤 Enter 또는 다른 칸을 클릭하면 적용됩니다 (`change` 이벤트).
- 공원명·지역·면적·개원일·관리부서 제목을 클릭하면 정렬합니다.
- 같은 제목을 다시 클릭하면 방향을 바꿉니다. 다른 제목은 오름차순부터 시작합니다.
- 공원 행 또는 공원명 버튼을 클릭하면 지도를 확대하고 팝업을 엽니다.
- 공원명 버튼은 키보드 Enter/Space도 지원합니다.

샘플은 서울 부근 좌표를 사용하는 **가상 공원 6개**입니다. 실제 133개 공원의 위치·이름·면적을 검증한 것이 아닙니다. 좌표 누락 1개가 있으므로 초기 결과는 **목록 6개, 마커 5개**입니다.

## 파일 구조

```text
README.md                             팀 저장소 기존 안내 (보존)
.gitignore / .nojekyll                 팀 저장소 기존 설정 (보존)
map_dashboard.py                      실제 담당 클래스 (팀 통합 대상)
run_demo.py                           로컬 HTTP 서버 실행 도우미
실행.cmd                               Windows 실행 도우미
demo/
  __init__.py
  index.html                          테스트 HTML: 합의한 6개 ID 유지
  style.css                           테스트 화면 전용 CSS
  main.py                             Mock 연결, 선택적 브라우저 테스트 실행
  mocks.py                            MockPark / MockParkManager / 가상 공원 6개
  pyscript.json                       데모 환경과 Python 파일 매핑
tests/
  __init__.py
  test_map_dashboard.py               CPython 단위 테스트
  browser_checks.py                   실제 DOM/Leaflet 통합 테스트
docs/mapdashboard/
  README.md                           이 문서
  integration.md                      팀 코드 연결 계약 및 예시
  test-results.md                     실제 검증 결과와 미검증 범위
  completion-report.md                독립 개발 완료 당시 보고서
  unit-tests.txt / browser-tests.txt   검증 출력 기록
  개발요약 10-28.txt                     팀원용 기능 확인 및 인수인계
```

## 자동 테스트

저장소 루트에서 실행합니다.

```powershell
python -m unittest discover -s tests -v
```

브라우저 테스트는 `python run_demo.py --test` 또는 실행 중인 데모 URL 끝에 `?test=1`을 붙여 실행합니다. 상단 상태와 화면 아래 테스트 결과의 `OK`/`FAILED`를 확인하세요. 테스트는 입력값을 변경하며, 끝나면 초기 화면으로 복구합니다.

PyScript 2026.7.3, Pyodide 0.29.0, Leaflet 1.9.4로 고정했습니다. Pyodide는 설정의 전체 URL로 지정했습니다. 단순 버전 문자열은 이 조합에서 상대 경로로 해석되어 초기화에 실패하는 것을 확인했습니다.

## 객체 간 책임

`MapDashboard(manager)` → `manager.get_districts()` / `manager.filter(...)` / `manager.sort_by(...)` → `park.get_location()` / `park.get_popup_html()` → 화면 갱신.

MapDashboard에는 공원 필터링·정렬 알고리즘이 없습니다. 생성자로 전달받은 Manager의 결과 순서를 그대로 사용합니다. 상태는 클래스 내부에서 관리하고, 이벤트는 고정된 부모 요소에 한 번만 연결하며, 마커는 전용 레이어를 비우고 다시 만듭니다.

팀 연결 방법과 숫자/빈값 전달 규칙은 [integration.md](integration.md), 테스트 결과는 [test-results.md](test-results.md), 팀원용 안내는 [개발요약 10-28.txt](<개발요약 10-28.txt>)를 참고하세요. PDF와 원본 엑셀은 개발 작업에 첨부되지 않아 요청문에 적힌 인터페이스를 기준으로 구현했습니다.

팀 통합 시 실제 [map_dashboard.py](../../map_dashboard.py)를 연결합니다. 데모 HTML로 팀의 실제 index.html을 덮어쓰지 마세요. 이 브랜치 공유 작업에는 main 병합, GitHub Pages 설정 변경, 최종 배포가 포함되지 않습니다.
