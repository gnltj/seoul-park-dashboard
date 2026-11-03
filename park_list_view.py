"""목록 표·표시 개수·정렬 상태와 공원 선택 알림을 담당한다."""


class ParkListView:
    COLUMNS = (
        ("name", "공원명"), ("district", "지역"), ("area", "면적"),
        ("open_date", "개원일"), ("department", "관리부서"),
    )

    def __init__(self):
        from js import document
        from pyodide.ffi import create_proxy

        self._document = document
        self._create_proxy = create_proxy
        self._container = document.getElementById("park-list")
        self._count = document.getElementById("park-count")
        if self._container is None or self._count is None:
            raise ValueError("필수 HTML ID가 없습니다: park-list 또는 park-count")
        if self._container.tagName not in ("TABLE", "DIV"):
            raise ValueError("park-list는 table 또는 div여야 합니다.")
        self.sort_key = "name"
        self.ascending = True
        self.shown_parks = []
        self._sort_handler = None
        self._select_handler = None
        self._listeners = {}
        self._headers = {}
        self._make_table()

    def show(self, parks):
        """현재 목록과 표시 수만 갱신한다. 지도 객체에는 접근하지 않는다."""
        self.shown_parks = list(parks)
        self._body.replaceChildren()
        for index, park in enumerate(self.shown_parks):
            row = self._document.createElement("tr")
            row.setAttribute("data-park-index", str(index))
            for key, _ in self.COLUMNS:
                cell = self._document.createElement("td")
                value = self._area_label(park) if key == "area" else self._label(getattr(park, key, None))
                if key == "name":
                    button = self._document.createElement("button")
                    button.type = "button"
                    button.textContent = value
                    cell.appendChild(button)
                else:
                    cell.textContent = value
                row.appendChild(cell)
            self._body.appendChild(row)
        if not self.shown_parks:
            row = self._document.createElement("tr")
            cell = self._document.createElement("td")
            cell.setAttribute("colspan", "5")
            cell.textContent = "조건에 맞는 공원이 없습니다."
            row.appendChild(cell)
            self._body.appendChild(row)
        self._count.textContent = str(len(self.shown_parks))
        self._update_headers()

    def get_sort(self):
        """Manager에 전달할 정렬 기준과 방향을 알려 준다."""
        return self.sort_key, self.ascending

    def on_sort_change(self, handler):
        """정렬 상태를 바꾼 뒤 호출할 함수를 등록한다."""
        self._sort_handler = handler
        self._listen("sort", self._handle_header_click)

    def on_select(self, handler):
        """행 선택 시 해당 Park 객체를 전달할 함수를 등록한다."""
        self._select_handler = handler
        self._listen("select", self._handle_row_click)

    def _make_table(self):
        self._container.replaceChildren()
        table = self._container
        if table.tagName != "TABLE":
            table = self._document.createElement("table")
            self._container.appendChild(table)
        head = self._document.createElement("thead")
        row = self._document.createElement("tr")
        for key, label in self.COLUMNS:
            th = self._document.createElement("th")
            th.setAttribute("scope", "col")
            button = self._document.createElement("button")
            button.type = "button"
            button.setAttribute("data-sort-key", key)
            th.appendChild(button)
            row.appendChild(th)
            self._headers[key] = (th, button, label)
        head.appendChild(row)
        table.appendChild(head)
        self._body = self._document.createElement("tbody")
        table.appendChild(self._body)
        self._update_headers()

    def _update_headers(self):
        for key, (th, button, label) in self._headers.items():
            selected = key == self.sort_key
            order = ("ascending" if self.ascending else "descending") if selected else "none"
            th.setAttribute("aria-sort", order)
            arrow = (" ▲" if self.ascending else " ▼") if selected else ""
            button.textContent = label + arrow

    def _listen(self, name, handler):
        if name not in self._listeners:
            proxy = self._create_proxy(handler)
            self._container.addEventListener("click", proxy)
            self._listeners[name] = proxy

    def _handle_header_click(self, event):
        header = self._event_element(event, "[data-sort-key]")
        if header is None:
            return
        key = header.getAttribute("data-sort-key")
        if key not in dict(self.COLUMNS):
            return
        self.ascending = not self.ascending if self.sort_key == key else True
        self.sort_key = key
        self._update_headers()
        if self._sort_handler is not None:
            self._sort_handler()

    def _handle_row_click(self, event):
        row = self._event_element(event, "[data-park-index]")
        if row is not None and self._select_handler is not None:
            index = int(row.getAttribute("data-park-index"))
            self._select_handler(self.shown_parks[index])

    def _event_element(self, event, selector):
        target = event.target
        if target is None or not hasattr(target, "closest"):
            return None
        element = target.closest(selector)
        return element if element is not None and self._container.contains(element) else None

    @staticmethod
    def _label(value):
        return "정보 없음" if value is None or value == "" else str(value)

    def _area_label(self, park):
        text = getattr(park, "area_text", None)
        if text is not None and text != "":
            return str(text)
        area = getattr(park, "area", None)
        return "정보 없음" if area is None else f"{area:,} ㎡"
