# 네 화면 클래스의 팀 연결 가이드

## 생성 및 시작

```python
from filter_panel import FilterPanel
from map_view import MapView
from park_list_view import ParkListView
from dashboard import Dashboard

dashboard = Dashboard(manager, FilterPanel(), MapView(), ParkListView())
dashboard.start()
```

실제 manager는 팀 DataLoader가 읽은 Park 목록으로 팀 ParkManager를 생성한 객체입니다. 데이터 로딩 후 화면 DOM과 Leaflet이 준비된 메인 스레드에서 생성합니다. dashboard 변수는 페이지가 유지되는 동안 보관합니다. 같은 객체의 start()는 중복 연결하지 않습니다.

기존 MapDashboard(manager)와 Park.get_popup_html() 계약은 폐기했습니다. 수정 계획서의 7개 클래스 가운데 이 브랜치의 실제 담당 클래스는 네 개입니다. 별도의 호환용 MapDashboard 클래스를 추가하지 않습니다.

## 화면 클래스 인터페이스

| 클래스 | 공개 메서드 |
|---|---|
| FilterPanel | __init__(), fill_districts(names), get_values(), on_change(handler) |
| MapView | __init__(), show(parks), make_popup(park), focus(park) |
| ParkListView | __init__(), show(parks), get_sort(), on_sort_change(handler), on_select(handler) |
| Dashboard | __init__(manager, filter_panel, map_view, list_view), start(), refresh(), on_park_selected(park) |

FilterPanel이 사용자 입력을 검증하고 값을 반환합니다. 잘못된 숫자, 음수, 무한대, 최소>최대는 None을 반환해 기존 결과를 유지합니다. 빈 조건은 빈 문자열이며 숫자 0으로 바꾸지 않습니다.

ParkListView가 COLUMNS, sort_key, ascending, shown_parks를 관리합니다. 같은 열 클릭은 방향 전환, 다른 열은 오름차순부터 시작하며 상태를 바꾼 뒤 handler()를 부릅니다. 행 클릭은 handler(park)로 실제 Park 인스턴스를 전달합니다.

Dashboard는 화면 객체의 메서드만 호출하며 js/DOM/Leaflet에 접근하지 않습니다. 화면 객체는 Dashboard를 import하거나 생성하지 않고 등록된 함수를 부릅니다. on_change/on_sort_change/on_select를 다시 등록해도 브라우저 리스너가 중복되지 않습니다.

## HTML 계약

| ID | 요소 | 담당 객체 |
|---|---|---|
| district | select | FilterPanel |
| min-area, max-area | input type=number, 권장 min=0 step=any | FilterPanel |
| map | CSS 높이가 지정된 div | MapView |
| park-list | table 또는 div (tbody 불가) | ParkListView |
| park-count | span/strong 등 개수 표시 요소 | ParkListView |

머리글은 ParkListView 생성 시 한 번 만들고 show()에서는 행과 개수만 갱신합니다. 표 외부 제목/안내문은 park-list 바깥에 둡니다. Leaflet CSS/JS와 PyScript를 로드해야 합니다. 기존 6개 ID는 변경하지 않았습니다.

## 데이터 객체 계약

Manager: get_districts(), filter(district, min_area, max_area), sort_by(parks, key, ascending). 정렬 키는 name, district, area, open_date, department입니다. 날짜를 비교값으로 바꾸거나 누락값을 뒤에 두는 정책은 Park/Manager 담당입니다.

```python
manager.filter("", "", "")          # 제한 없음
manager.filter("종로구", 1000.0, "") # 최소 면적만 지정
manager.filter("", "", 0.0)         # 최대 면적 0
```

Park: get_location()은 [위도, 경도]를 반환하며, 없으면 None 또는 [None, None]을 사용할 수 있습니다. get_sort_value(key)는 Manager가 사용합니다. 화면 목록 속성은 name, district, area_text, area, open_date, department입니다. 이미 정제된 숫자와 문자열만 표시하며 엑셀이나 원본 면적 문자열을 해석하지 않습니다.

MapView.make_popup()은 Park의 name, district, address, area_text/area, open_date, department, phone, facilities, plants, summary, directions, notes, guide_map, image, link를 읽습니다. 없는 값은 빈칸입니다. 일반 텍스트를 HTML escape하고 링크는 http/https 주소만 사용합니다. 이미지·안내도는 img 태그 대신 링크로 표시합니다. 긴 팝업은 최대 높이 300px 안에서 스크롤합니다.

마커는 Park 객체의 동일성을 기준으로 연결합니다. id 속성이 중복되거나 Park가 해시 불가능한 객체여도 선택한 공원으로 연결합니다. 유효한 좌표가 없는 공원은 마커만 생략하고 목록/개수에는 포함합니다.

## PyScript 파일 매핑

실제 팀 설정에 다음 네 파일이 로드되어야 합니다. 팀원의 다른 매핑과 설정을 유지하세요.

```toml
[files]
"./filter_panel.py" = "./filter_panel.py"
"./map_view.py" = "./map_view.py"
"./park_list_view.py" = "./park_list_view.py"
"./dashboard.py" = "./dashboard.py"
```

팀원이 작성한 main.py와 HTML/PyScript 설정은 별도 임시 폴더에서 그대로 연결해 확인했습니다. 이 브랜치에서는 그 파일을 복사해 넣거나 수정하지 않습니다. demo/의 main.py와 Mock을 실제 팀 진입 코드로 덮어쓰지 마세요.
