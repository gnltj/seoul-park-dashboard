"""공원 데이터 처리는 Manager에 위임하고 지도와 사용자 이벤트만 담당한다."""

from math import isfinite


class MapDashboard:
    COLUMNS = (
        ("name", "공원명"),
        ("district", "지역"),
        ("area", "면적"),
        ("open_date", "개원일"),
        ("department", "관리부서"),
    )
    SEOUL_CENTER = (37.5665, 126.9780)

    def __init__(self, manager):
        """협력 객체와 화면 상태를 초기화한다. 브라우저 작업은 start에서 한다."""
        self.manager = manager
        self.sort_key = "name"
        self.ascending = True
        self.parks = []
        self._started = False
        self._elements = {}
        self._listeners = []
        self._map = None
        self._marker_layer = None
        self._markers = {}

    def start(self):
        """합의한 HTML 요소에 지도와 이벤트를 한 번만 연결한다."""
        if self._started:
            return

        # CPython에서는 모듈을 import할 수 있고, 실행 시에만 Pyodide가 필요하다.
        from js import L, Object, document
        from pyodide.ffi import create_proxy, to_js

        self._document = document
        self._leaflet = L
        self._to_js = to_js
        self._object = Object
        required = ("map", "district", "min-area", "max-area", "park-list", "park-count")
        elements = {name: document.getElementById(name) for name in required}
        missing = [name for name, element in elements.items() if element is None]
        if missing:
            raise ValueError("필수 HTML ID가 없습니다: " + ", ".join(missing))
        self._elements = elements

        district = elements["district"]
        district.replaceChildren()
        self._add_option(district, "", "전체 구")
        for name in self.manager.get_districts():
            self._add_option(district, name, name)

        self._map = L.map(elements["map"]).setView(to_js(list(self.SEOUL_CENTER)), 11)
        L.tileLayer(
            "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            self._js_options({
                "maxZoom": 19,
                "attribution": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            }),
        ).addTo(self._map)
        self._marker_layer = L.layerGroup().addTo(self._map)

        # 콜백 프록시를 보관해 Pyodide의 임시 프록시 소멸을 방지한다.
        for name in ("district", "min-area", "max-area"):
            proxy = create_proxy(self.on_filter_change)
            elements[name].addEventListener("change", proxy)
            self._listeners.append(proxy)
        # 행/머리글이 교체되어도 고정된 부모 요소의 리스너를 계속 사용한다.
        for handler in (self.on_header_click, self.on_row_click):
            proxy = create_proxy(handler)
            elements["park-list"].addEventListener("click", proxy)
            self._listeners.append(proxy)

        self._started = True
        self.refresh()

    def refresh(self):
        """입력 확인 → 필터 위임 → 정렬 위임 → 마커/목록/개수 갱신."""
        if not self._started:
            raise RuntimeError("start()를 먼저 호출하세요.")
        filters = self._read_filters()
        if filters is None:
            return  # 잘못된 입력은 브라우저에 알리고 기존 결과를 유지한다.
        filtered = self.manager.filter(*filters)
        self.parks = list(self.manager.sort_by(filtered, self.sort_key, self.ascending))
        self.draw_markers(self.parks)
        self.draw_list(self.parks)
        self._elements["park-count"].textContent = str(len(self.parks))

    def draw_markers(self, parks):
        """기존 마커를 비우고 Park가 제공한 위치와 팝업으로 다시 그린다."""
        self._marker_layer.clearLayers()
        self._markers.clear()
        for index, park in enumerate(parks):
            location = self._valid_location(park.get_location())
            if location is None:
                continue  # 좌표가 없어도 목록과 전체 결과 개수에는 포함된다.
            marker = self._leaflet.marker(self._to_js(location))
            marker.bindPopup(park.get_popup_html()).addTo(self._marker_layer)
            self._markers[index] = marker

    def draw_list(self, parks):
        """5개 열을 만든다. 일반 데이터는 textContent로 출력한다."""
        container = self._elements["park-list"]
        container.replaceChildren()
        # 팀원은 table 자체 또는 목록용 div에 park-list ID를 지정하면 된다.
        table = container if container.tagName == "TABLE" else self._document.createElement("table")
        if table is not container:
            container.appendChild(table)
        head = self._document.createElement("thead")
        header_row = self._document.createElement("tr")
        for key, label in self.COLUMNS:
            th = self._document.createElement("th")
            th.setAttribute("scope", "col")
            selected = key == self.sort_key
            order = ("ascending" if self.ascending else "descending") if selected else "none"
            th.setAttribute("aria-sort", order)
            button = self._document.createElement("button")
            button.type = "button"
            button.setAttribute("data-sort-key", key)
            arrow = (" ▲" if self.ascending else " ▼") if selected else ""
            button.textContent = label + arrow
            th.appendChild(button)
            header_row.appendChild(th)
        head.appendChild(header_row)
        table.appendChild(head)

        body = self._document.createElement("tbody")
        for index, park in enumerate(parks):
            row = self._document.createElement("tr")
            row.setAttribute("data-park-index", str(index))
            for key, _ in self.COLUMNS:
                cell = self._document.createElement("td")
                value = self._area_label(park) if key == "area" else self._label(getattr(park, key, None))
                if key == "name":
                    # 기본 button을 사용하므로 Enter/Space로도 지도 이동이 가능하다.
                    button = self._document.createElement("button")
                    button.type = "button"
                    button.textContent = value
                    if index not in self._markers:
                        button.setAttribute("title", "좌표 정보가 없어 지도 이동이 불가능합니다.")
                    cell.appendChild(button)
                else:
                    cell.textContent = value
                row.appendChild(cell)
            body.appendChild(row)
        if not parks:
            row = self._document.createElement("tr")
            cell = self._document.createElement("td")
            cell.setAttribute("colspan", "5")
            cell.textContent = "조건에 맞는 공원이 없습니다."
            row.appendChild(cell)
            body.appendChild(row)
        table.appendChild(body)

    def on_filter_change(self, event=None):
        """필터의 change 이벤트에서 현재 입력을 다시 읽는다."""
        self.refresh()

    def on_header_click(self, event=None):
        """같은 열은 방향을 전환하고 다른 열은 오름차순부터 시작한다."""
        header = self._event_element(event, "[data-sort-key]")
        if header is None:
            return
        key = header.getAttribute("data-sort-key")
        if key not in dict(self.COLUMNS):
            return
        self.ascending = not self.ascending if self.sort_key == key else True
        self.sort_key = key
        self.refresh()

    def on_row_click(self, event=None):
        """현재 화면의 행에 대응하는 마커로 이동하고 팝업을 연다."""
        row = self._event_element(event, "[data-park-index]")
        if row is None:
            return
        index = int(row.getAttribute("data-park-index"))
        marker = self._markers.get(index)
        if marker is not None:
            # 연속 클릭 중 이전 확대 애니메이션이 남지 않도록 즉시 이동한다.
            self._map.setView(marker.getLatLng(), 15, self._js_options({"animate": False}))
            marker.openPopup()

    def _read_filters(self):
        """빈 면적은 빈 문자열로 보존하고 유효한 숫자 입력만 float로 바꾼다."""
        values = []
        for name in ("min-area", "max-area"):
            element = self._elements[name]
            element.setCustomValidity("")
            raw = element.value
            try:
                value = "" if raw == "" else float(raw)
                if value != "" and (not isfinite(value) or value < 0):
                    raise ValueError
            except (TypeError, ValueError):
                element.setCustomValidity("면적은 0 이상의 숫자로 입력하세요.")
                element.reportValidity()
                return None
            if not element.checkValidity():
                element.reportValidity()
                return None
            values.append(value)
        if all(value != "" for value in values) and values[0] > values[1]:
            element = self._elements["max-area"]
            element.setCustomValidity("최대 면적은 최소 면적 이상이어야 합니다.")
            element.reportValidity()
            return None
        return (self._elements["district"].value, *values)

    def _event_element(self, event, selector):
        if event is None:
            return None
        target = event.target
        if target is None or not hasattr(target, "closest"):
            return None
        element = target.closest(selector)
        if element is not None and self._elements["park-list"].contains(element):
            return element
        return None

    def _add_option(self, select, value, label):
        option = self._document.createElement("option")
        option.value = value
        option.textContent = label
        select.appendChild(option)

    def _js_options(self, options):
        return self._to_js(options, dict_converter=self._object.fromEntries)

    @staticmethod
    def _label(value):
        return "정보 없음" if value is None or value == "" else str(value)

    def _area_label(self, park):
        # 이미 정제된 숫자/표시 문자열만 사용하며 원본 면적 문자열은 해석하지 않는다.
        text = getattr(park, "area_text", None)
        if text is not None and text != "":
            return str(text)
        area = getattr(park, "area", None)
        return "정보 없음" if area is None else f"{area:,} ㎡"

    @staticmethod
    def _valid_location(location):
        if location is None:
            return None
        try:
            if len(location) != 2:
                return None
            lat, lng = map(float, location)
            if isfinite(lat) and isfinite(lng) and -90 <= lat <= 90 and -180 <= lng <= 180:
                return [lat, lng]
        except (TypeError, ValueError, OverflowError):
            pass
        return None
