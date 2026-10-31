# 내 서울 공원 길라잡이: 133개 공원을 한눈에

서울시 주요 공원 133곳을 지도와 목록으로 보여주는 대시보드입니다. 구와 면적으로 원하는 공원만 골라 보고, 목록에서 원하는 항목으로 정렬하고, 공원을 누르면 지도가 그 위치로 이동합니다.

- 대시보드 주소: https://gnltj.github.io/seoul-park-dashboard/
- 사용 기술: Python, [PyScript](https://pyscript.net/)(브라우저에서 Python 실행), [Leaflet](https://leafletjs.com/)(지도), Python `csv` 모듈

## 1. 프로젝트 개요

대시보드는 Python으로 구현했고, PyScript를 이용해 github.io 페이지를 연 브라우저에서 Python 코드가 직접 실행됩니다. 엑셀 데이터는 CSV 파일로 변환해 Python의 `csv` 모듈로 읽고, Leaflet 지도에 서울시 주요 공원 133곳을 표시합니다. 공원을 클릭하면 공원 데이터가 팝업으로 나타나고, 지도 옆 목록 패널에서는 공원명·지역·면적·개원일·관리부서 중 원하는 항목을 눌러 오름차순·내림차순으로 정렬할 수 있습니다.

## 2. 실행 방법

### 배포된 사이트에서 보기

https://gnltj.github.io/seoul-park-dashboard/ 에 접속합니다. 처음에는 브라우저가 Python 실행 환경을 내려받느라 시간이 걸릴 수 있습니다.

### 내 컴퓨터에서 실행하기

```
git clone https://github.com/gnltj/seoul-park-dashboard.git
cd seoul-park-dashboard
python -m http.server 8000
```

Windows에서 `python`이 실행되지 않으면 `py -3 -m http.server 8000`을 사용합니다. 그다음 브라우저에서 http://localhost:8000 을 열고, 끝낼 때는 터미널에서 `Ctrl+C`를 누릅니다.

- `index.html`을 파일 탐색기에서 더블클릭해 열면 동작하지 않습니다. PyScript가 Python 파일과 `parks.csv`를 HTTP로 가져오므로 위처럼 로컬 서버가 필요합니다.
- PyScript, Leaflet, OpenStreetMap 배경 지도를 불러오므로 인터넷 연결이 필요합니다.

### 배포 방법 (GitHub Pages)

1. 저장소의 **Settings → Pages**로 이동합니다.
2. **Build and deployment**의 Source를 **Deploy from a branch**로 두고, Branch는 `main`, 폴더는 `/ (root)`로 선택한 뒤 **Save**를 누릅니다.
3. 잠시 뒤 위의 대시보드 주소에서 사이트를 확인합니다.

저장소 루트의 `.nojekyll` 파일 덕분에 GitHub Pages가 Jekyll 처리를 하지 않고 파일을 그대로 배포합니다. 그래서 `main` 브랜치에 푸시하면 사이트가 갱신됩니다.

## 3. 사용 데이터

| 구분 | 데이터 | 내용 |
|---|---|---|
| 기본 데이터 | 서울시 주요 공원 현황 | 엑셀 데이터를 CSV(`parks.csv`)로 변환해 사용합니다. 공원 133곳. |
| 추가 데이터 | 누락된 위치 데이터 | 지도 API로 위치를 보여주려면 WGS84 좌표가 필요한데, 좌표가 없는 공원은 좌표를 임의로 보충했습니다(예: 서울로7017). |

- 엑셀 값을 그대로 처리하기 때문에 실제 수치와 다를 수 있습니다.
- 면적이 없는 공원은 5곳, 개원일이 없는 공원은 8곳이며 정렬할 때 항상 맨 아래에 놓입니다.
- 읽어 들일 때 빈 지역은 주소에서 채우고, `http` 링크는 `https`로 바꾸고, 면적 글자에서는 쉼표를 지운 뒤 앞부분 숫자만 꺼냅니다.

## 4. 클래스 설계 및 객체 간 상호작용

### 클래스 7개

| 클래스 | 맡은 일 | 주요 메서드 |
|---|---|---|
| `Park` | 공원 한 곳의 정보를 담고, 위치와 정렬에 쓸 값을 돌려줌 | `get_location()`, `get_sort_value(key)` |
| `DataLoader` | CSV 파일을 읽어 빈칸 등을 정리하고 `Park` 객체 목록을 만듦 | `load()`, `clean(row)`, `to_number(text)` |
| `ParkManager` | `Park` 목록을 보관하고, 조건에 맞는 공원을 골라 정렬해 줌 | `get_districts()`, `filter(district, min_area, max_area)`, `sort_by(parks, key, ascending)` |
| `FilterPanel` | 구 드롭다운과 면적 입력칸을 맡아, 사용자가 고른 조건을 읽어 줌 | `fill_districts(names)`, `get_values()`, `on_change(handler)` |
| `MapView` | Leaflet 지도에 마커와 팝업을 그리고, 고른 공원으로 지도를 옮김 | `show(parks)`, `make_popup(park)`, `focus(park)` |
| `ParkListView` | 공원 목록 표를 그리고, 정렬 기준과 표시 중인 공원 수를 관리함 | `show(parks)`, `get_sort()`, `on_sort_change(handler)`, `on_select(handler)` |
| `Dashboard` | `ParkManager`와 화면 객체 3개를 연결해 전체 흐름을 지휘함. 브라우저를 직접 다루지 않음 | `start()`, `refresh()`, `on_park_selected(park)` |

`main.py`는 클래스가 아니라 시작 파일입니다. `Park`를 뺀 여섯 클래스의 객체를 만들어 서로 연결합니다(`Park` 객체는 `DataLoader`가 만듭니다).

### 클래스 관계

- **`DataLoader` → `Park` (생성)**: CSV 1행이 `Park` 객체 1개가 됩니다.
- **`ParkManager` → `Park` (보관·사용)**: `Park` 목록을 넘겨받아 보관하고, `get_sort_value()`로 정렬합니다.
- **`Dashboard` → `ParkManager` (요청)**: 조건을 넘겨 `filter()`, `sort_by()`로 목록을 받습니다. 직접 거르거나 정렬하지 않습니다.
- **`Dashboard` → `FilterPanel`·`MapView`·`ParkListView` (지시)**: 조건과 정렬 기준을 읽어 오고, 받은 목록을 그리라고 시킵니다. `Dashboard`는 화면을 직접 만지지 않습니다.
- **`MapView`·`ParkListView` → `Park` (사용)**: 마커·팝업·목록 행을 만들 때 `get_location()`과 공원 속성을 읽습니다.
- **화면 객체 → `Dashboard` (알림)**: 입력이 바뀌면 `start()`에서 넘겨받은 함수(`refresh` 등)를 부릅니다. 화면 객체는 `Dashboard` 클래스를 직접 알지 못합니다.

### 설계 원칙

- **단일 책임**: 클래스마다 고쳐야 하는 이유가 하나뿐이 되도록 나눴습니다. 처음 설계의 `MapDashboard` 하나가 맡던 입력칸·지도·목록·흐름 조정을 `FilterPanel`, `MapView`, `ParkListView`, `Dashboard`로 나누고, 팝업 내용 만들기는 `Park`에서 `MapView`로 옮겼습니다.
- **생성자로 협력 객체 받기**: `Dashboard`는 함께 일할 객체를 직접 만들지 않고 `main.py`에서 넘겨받습니다. 그래서 브라우저 없이 가짜 객체로도 `Dashboard`를 시험할 수 있습니다.
- **한 방향 의존**: `Park`는 다른 클래스를 부르지 않고, 화면 객체는 `Dashboard`를 모릅니다. 브라우저(`js`)를 다루는 클래스는 화면 클래스 3개뿐입니다.

### 처리 흐름

| 단계 | 상황 | 일어나는 일 |
|---|---|---|
| 1~2 | `parks.csv` 읽기 | `DataLoader.load()`가 CSV를 한 줄씩 읽고, `clean(row)`·`to_number()`로 정리해 `Park` 객체 133개를 만듭니다. |
| 3 | 목록 보관 | `main.py`가 `Park` 목록을 `ParkManager`에 넘깁니다. |
| 4 | 화면 객체 준비 | `main.py`가 `FilterPanel()`, `MapView()`, `ParkListView()`를 만들고 `Dashboard(manager, 화면 객체 3개)`를 만듭니다. |
| 5 | 페이지 첫 로드 | `Dashboard.start()`가 `get_districts()`로 구 드롭다운을 채우고, 화면 객체의 입력·정렬·선택 이벤트를 연결합니다. |
| 6 | 화면 그리기 | `refresh()`가 조건과 정렬 기준을 읽고 `filter()` → `sort_by()`로 목록을 받아 `MapView.show()`, `ParkListView.show()`로 지도와 목록을 다시 그립니다. 처음에는 필터 없이 공원명 오름차순이라 마커 133개, 목록 133행이 나옵니다. |
| 7 | 구 선택·면적 입력, 머리글 클릭 | 입력이 바뀌면 연결해 둔 `refresh()`가 불려 6단계와 같은 흐름으로 다시 그립니다. 머리글을 누르면 정렬 기준·방향을 바꾼 뒤 `refresh()`를 부릅니다. |
| 8 | 마커·목록 행 클릭 | 마커는 팝업이 자동으로 열립니다. 목록 행은 `on_select()` → `on_park_selected(park)` → `MapView.focus(park)`로 지도를 그 위치로 옮기고 팝업을 엽니다. |

## 5. 대시보드 기능 설명

| 화면 | 보여주는 것 | 사용법 |
|---|---|---|
| 메인 지도 | 공원 위치 마커 | 확대·축소·이동할 수 있고, 마커를 누르면 팝업이 열립니다. 좌표가 없는 공원은 마커를 건너뜁니다. |
| 공원 목록 패널 | 공원명·지역·면적·개원일·관리부서 표, 표시 중인 공원 수 | 머리글을 누르면 오름차순, 같은 머리글을 다시 누르면 내림차순으로 정렬합니다. 값이 없는 공원은 항상 맨 아래에 놓입니다. 행을 누르면 지도가 그 공원으로 이동합니다. |
| 공원 정보 팝업 | 공원명, 주소, 면적, 개원일, 관리부서, 전화번호, 주요시설, 안내도·이미지·바로가기 링크 | 값이 없으면 빈칸으로 두고, 이미지·안내도·바로가기는 링크로 표시합니다. |
| 구 선택 필터 | 구 드롭다운 | 고른 구의 공원만 지도와 목록에 표시합니다. '전체'를 고르면 모든 구를 보여줍니다. |
| 면적 범위 필터 | 최소·최대 면적 입력칸(㎡) | 범위 안의 공원만 표시합니다. 칸을 비우면 그쪽 제한이 없고, 면적 조건을 걸면 면적 값이 없는 공원은 제외됩니다. |

## 6. 파일 구성

| 파일 | 역할 |
|---|---|
| `index.html` | 화면의 틀(필터, 지도, 목록 자리)과 Leaflet·PyScript 불러오기 |
| `style.css` | 화면 배치와 스타일 |
| `pyscript.toml` | 브라우저 안으로 불러올 Python 파일·`parks.csv`와 Python 실행 환경 설정 |
| `main.py` | 시작 파일: 객체를 만들고 연결 (클래스 아님) |
| `parks.csv` | 서울시 주요 공원 현황 133곳 |
| `park.py` | `Park` |
| `data_loader.py` | `DataLoader` |
| `park_manager.py` | `ParkManager` |
| `filter_panel.py` | `FilterPanel` |
| `map_view.py` | `MapView` |
| `park_list_view.py` | `ParkListView` |
| `dashboard.py` | `Dashboard` |
| `.nojekyll` | GitHub Pages가 Jekyll 처리를 하지 않게 함 |
