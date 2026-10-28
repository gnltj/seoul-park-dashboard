# 팀원 코드 연결 가이드

## 실제 팀 프로젝트에 필요한 코드

본체는 `map_dashboard.py` 하나입니다. 실제 ParkManager가 준비되면 팀의 Python 진입 코드에서 다음과 같이 연결합니다.

```python
from map_dashboard import MapDashboard

# manager는 팀원이 생성한 실제 ParkManager 인스턴스입니다.
dashboard = MapDashboard(manager)
dashboard.start()
```

`dashboard`는 모듈 전역 등 페이지가 살아 있는 동안 유지되는 변수에 저장하세요. 페이지에 지도 하나당 인스턴스 하나를 사용합니다. 같은 인스턴스의 `start()`는 반복 호출해도 지도와 이벤트를 다시 만들지 않습니다. `refresh()`는 `start()` 이후 호출합니다.

`demo/main.py`, `demo/mocks.py`, `demo/index.html`, `demo/style.css`는 실제 팀 코드를 대체하지 않습니다. 기존 팀원의 파일을 덮어쓰지 마세요. 필요하면 테스트/문서를 별도 개발 자료로 보관합니다.

## HTML 계약 (ID 변경 없음)

| ID | 요소 계약 |
|---|---|
| `map` | 지도용 div. 팀 CSS에서 높이 지정 필수 (예: 500px) |
| `district` | select. start()가 전체 구 옵션 및 get_districts() 결과를 채움 |
| `min-area` | input type="number", 권장 min="0" step="any" |
| `max-area` | input type="number", 권장 min="0" step="any" |
| `park-list` | **table 또는 div**. 내부 머리글·행은 Dashboard가 생성/교체 |
| `park-count` | span 등 textContent로 개수를 표시할 요소 |

`park-list`를 tbody로 지정하지 마세요. 5개 열의 thead/tbody 전체를 생성하는 계약입니다. 목록 외곽의 제목/안내문은 `park-list` 바깥에 두세요. 머리글의 정렬 키는 `name`, `district`, `area`, `open_date`, `department`이며, 면적 표시에는 `area_text`를 우선 사용합니다.

Leaflet CSS/JS와 PyScript를 HTML에서 로드하고, DOM을 직접 다루므로 Python 스크립트를 **메인 스레드**에서 실행합니다 (`worker` 속성 없음). 데모와 동일한 버전의 예:

```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://pyscript.net/releases/2026.7.3/core.css">
<script type="module" src="https://pyscript.net/releases/2026.7.3/core.js"></script>
<!-- 합의한 6개 ID의 요소 배치 후 -->
<script type="py" src="main.py" config="pyscript.json"></script>
```

팀 설정에 `map_dashboard.py`의 파일 매핑을 **추가**하세요. 팀원의 다른 설정은 유지합니다. 아래는 팀 HTML·설정·Python 파일이 같은 디렉터리에 있을 때의 예입니다.

```json
{
  "interpreter": "https://cdn.jsdelivr.net/pyodide/v0.29.0/full/pyodide.mjs",
  "files": {
    "./map_dashboard.py": "./map_dashboard.py"
  }
}
```

Manager/Park 등 팀원이 작성한 로컬 Python 모듈도 해당 팀 설정을 통해 브라우저 가상 파일시스템에 로드되어 있어야 합니다. 실제 경로는 팀 폴더 구조에 맞춰 설정합니다. GitHub Pages에서도 상대 경로를 사용합니다. 최종 배포는 이번 작업 범위에 포함하지 않았습니다.

## ParkManager 계약

| 메서드 | 입력 및 결과 |
|---|---|
| `get_districts()` | 표시할 고유 구 이름 문자열의 iterable. 빈 구 옵션은 Dashboard가 추가 |
| `filter(district, min_area, max_area)` | district는 문자열, 전체 선택은 `""`. 면적은 빈 문자열 `""` 또는 0 이상 유한한 float |
| `sort_by(parks, key, ascending)` | filter 결과를 그대로 전달. key는 위 5개 키, ascending은 bool. 정렬된 Park iterable 반환 |

중요한 예:

```python
manager.filter("", "", "")             # 면적 제한 없음
manager.filter("종로구", 1000.0, "")    # 최소 면적만 지정
manager.filter("", "", 0.0)            # 실제 최대 면적 0 지정
```

빈 입력을 0으로 바꾸지 않습니다. 숫자로 변환하는 것은 **사용자의 면적 입력**뿐입니다. 원본 엑셀의 면적 문자열을 해석하거나 정제하지 않습니다. 잘못된 숫자·음수·최소>최대는 입력 오류로 알리고 기존 결과를 유지하며 Manager를 호출하지 않습니다.

필터 결과에 면적/날짜 누락 공원을 포함할지, 결측값을 어디에 정렬할지, 구 이름을 어떤 순서로 제공할지는 **실제 ParkManager의 책임**입니다. Demo의 정책은 팀 계약이 아닙니다. filter/sort_by는 동기 메서드이며 결과를 반환해야 합니다. 비동기 데이터 로딩이 있다면 로딩 완료 후 Dashboard를 시작하세요.

## Park 계약

- `get_location()` → `[위도, 경도]`, 좌표가 없으면 `None` 또는 `[None, None]`.
- `get_popup_html()` → Leaflet에 전달할 HTML 문자열. HTML을 제공하는 Park가 텍스트를 escape하거나 정제해야 합니다.
- 목록 표시 속성: `name`, `district`, `area_text`, `area`, `open_date`, `department`.
- `area`는 이미 정제된 숫자 또는 `None`; `area_text`가 없으면 숫자에 천 단위 구분과 ㎡ 단위를 붙여 표시합니다. 값이 0이면 `0 ㎡`로 표시합니다.
- `get_sort_value(key)`는 실제 Manager가 사용할 메서드입니다. Dashboard가 직접 호출하거나 정렬하지 않습니다.
- `id`, `address`, `lat`, `lng`는 요청된 Park의 예상 속성입니다. Dashboard는 직접 좌표 속성/원본 좌표 열을 읽지 않습니다.

좌표는 Leaflet에 넘길 수 있는 유한한 위도(-90~90)/경도(-180~180)인지 확인만 합니다. 좌표 보완/정제나 순서 교환을 하지 않습니다. 유효한 좌표가 없는 공원도 목록 및 `park-count`에는 포함되며 행을 눌러도 오류 없이 지도가 유지됩니다.

행과 마커의 연결은 현재 결과의 인덱스로 관리하므로 Park.id가 숫자/문자열이거나 동일한 id가 있는 경우에도 잘못된 공원을 찾지 않습니다. 필터/정렬 후에는 연결을 다시 만듭니다.

## 교체할 부분과 유지할 부분

1. 테스트용 Mock Manager 생성 부분을 실제 Manager 인스턴스 연결로 교체합니다.
2. 팀 HTML에 6개 ID와 `park-list` 요소 타입, 지도 높이가 맞는지 확인합니다.
3. 팀 PyScript 설정에 본체와 팀 모듈 경로를 추가합니다.
4. 실제 Manager의 인자와 정렬 키가 위 계약과 일치하는지 확인합니다.
5. 실제 Park의 좌표 순서와 팝업 HTML 계약을 확인합니다.

계약이 일치하면 `map_dashboard.py` 본체를 수정할 필요가 없습니다. 실제 PDF는 첨부되지 않아 PDF 기준 인터페이스 일치는 아직 확인하지 못했습니다.

## 참고한 공식 문서

- [PyScript 2026.7.3 시작](https://docs.pyscript.net/2026.7.3/)
- [PyScript 파일/인터프리터 설정](https://docs.pyscript.net/2026.7.3/user-guide/configuration/)
- [Pyodide Python/JavaScript 자료형 변환](https://pyodide.org/en/stable/usage/type-conversions.html)
- [Leaflet 1.9.4 API](https://leafletjs.com/reference.html)
