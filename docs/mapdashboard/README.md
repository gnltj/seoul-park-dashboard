# MapDashboard 화면 기능 4개 클래스

2026-11-02 수정 계획서의 7개 클래스 설계에 맞춰 기존 MapDashboard를 FilterPanel, MapView, ParkListView, Dashboard로 분리했습니다. 이 네 클래스가 김건우 담당 범위입니다. Park, DataLoader, ParkManager는 팀원 담당이며 실제 구현을 이 브랜치에 추가하지 않았습니다.

## 실행

모든 명령은 저장소 루트(run_demo.py가 있는 폴더) 기준입니다. Python 3.10 이상과 인터넷이 필요하며 pip 패키지 설치는 필요하지 않습니다.

```powershell
python run_demo.py
python run_demo.py --test
# 기본 포트가 사용 중이면
python run_demo.py --test --port 8768
```

Windows에서는 루트의 [실행.cmd](../../실행.cmd)를 더블클릭해도 됩니다. py -3를 우선 사용하고 없으면 PATH의 python을 사용합니다. 종료는 실행 창에서 Ctrl+C입니다. HTML을 파일로 직접 열지 말고 로컬 HTTP 서버를 사용하세요. 이 문서 폴더에서 서버를 실행하지 마세요.

샘플은 가상 공원 6개이며 초기 목록/개수는 6개, 마커는 5개입니다. 빈 면적은 제한 없음, 입력한 0은 실제 조건 0으로 구분합니다. 면적 입력 후 Enter 또는 다른 칸을 클릭하면 적용됩니다.

## 담당 파일과 책임

| 파일 | 클래스와 역할 |
|---|---|
| [filter_panel.py](../../filter_panel.py) | FilterPanel: 구·면적 입력 읽기/검증 및 변경 알림 |
| [map_view.py](../../map_view.py) | MapView: Leaflet 지도, 마커, 팝업 HTML, 선택 공원 이동 |
| [park_list_view.py](../../park_list_view.py) | ParkListView: 목록, 결과 개수, 정렬 상태, Park 선택 알림 |
| [dashboard.py](../../dashboard.py) | Dashboard: 위 화면 객체와 Manager의 협력 흐름 조정 |

기존 map_dashboard.py는 위 네 파일로 대체했습니다. 호환용 MapDashboard 클래스를 남겨 8번째 클래스로 만들지 않았습니다. 이전 코드는 Git 이력에 있습니다.

Dashboard는 js/DOM/Leaflet을 import하지 않습니다. 화면 객체도 Dashboard를 import하지 않으며 전달받은 함수를 호출합니다. 필터와 정렬 알고리즘은 Manager에만 있습니다.

## 독립 데모와 테스트

- demo/main.py: 네 객체를 생성해 MockParkManager와 연결하는 테스트 진입 코드
- demo/mocks.py: 테스트 전용 MockPark/MockParkManager와 가상 공원 6개. get_popup_html() 없음
- demo/index.html, style.css: 테스트 전용 화면. 실제 팀 화면을 대체하지 않음
- demo/pyscript.json: 네 클래스 및 테스트 Python 파일 매핑
- tests/test_dashboard.py: 브라우저 없는 흐름 테스트
- tests/test_views.py: 입력, 팝업, 정렬/선택 계약 테스트
- tests/browser_checks.py: 실제 PyScript·DOM·Leaflet의 22개 시나리오

```powershell
python -m unittest discover -s tests -v
```

브라우저 테스트는 --test 또는 데모 URL 끝에 ?test=1로 실행합니다. 상단 상태와 하단 OK/FAILED를 확인하세요. Python 33개 및 브라우저 22개 결과는 [검증 기록](test-results.md)에 있습니다. PyScript 2026.7.3, Pyodide 0.29.0, Leaflet 1.9.4를 사용합니다.

## 팀 코드 연결

```python
from dashboard import Dashboard
from filter_panel import FilterPanel
from map_view import MapView
from park_list_view import ParkListView

# manager는 팀원이 생성한 실제 ParkManager 객체
dashboard = Dashboard(manager, FilterPanel(), MapView(), ParkListView())
dashboard.start()
```

팀장님이 올린 main.py의 생성자와 import 이름에 맞춘 구조입니다. 실제 main.py, index.html, CSS, PyScript 설정과 데이터 파일은 팀원 담당이므로 이 작업에서 수정하지 않습니다.

구·면적 변경 또는 머리글 클릭 → Dashboard.refresh() → FilterPanel.get_values()/ParkListView.get_sort() → Manager.filter()/sort_by() → MapView.show()/ParkListView.show().

행 클릭 → ParkListView가 Park 객체 전달 → Dashboard.on_park_selected(park) → MapView.focus(park).

팝업은 MapView가 Park의 속성으로 만듭니다. 누락값은 빈칸, 이미지/안내도/바로가기는 링크입니다. 긴 설명은 팝업 내부 스크롤을 사용합니다. 목록의 누락값은 기존처럼 정보 없음으로 표시합니다.

상세 계약은 [통합 가이드](integration.md), 팀원용 설명은 [개발요약 10-28.txt](<개발요약 10-28.txt>)를 참고하세요. 검수 원본과 팀원 코드는 보존합니다.

사용자가 확인한 [클래스 구조 변경 요약](<MapDashboard_변경사항_2026-11-02_검수용.txt>)도 같은 폴더에 보관합니다. 바탕화면에서 최종 확인한 파일의 이름과 내용을 유지했습니다.
