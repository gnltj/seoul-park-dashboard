"""구·면적 입력과 변경 알림을 담당한다. 공원 데이터는 처리하지 않는다."""

from math import isfinite


class FilterPanel:
    def __init__(self):
        from js import document
        from pyodide.ffi import create_proxy

        self._document = document
        self._create_proxy = create_proxy
        self.district_select = document.getElementById("district")
        self.min_input = document.getElementById("min-area")
        self.max_input = document.getElementById("max-area")
        for name, element in (("district", self.district_select), ("min-area", self.min_input), ("max-area", self.max_input)):
            if element is None:
                raise ValueError(f"필수 HTML ID가 없습니다: {name}")
        self._change_handler = None
        self._listeners = []

    def fill_districts(self, names):
        """전체 옵션과 Manager가 제공한 구 목록을 채운다."""
        self.district_select.replaceChildren()
        for value, label in [("", "전체"), *((name, name) for name in names)]:
            option = self._document.createElement("option")
            option.value = value
            option.textContent = label
            self.district_select.appendChild(option)

    def get_values(self):
        """빈 입력은 빈 문자열, 유효 숫자는 float, 잘못된 조건은 None을 반환한다."""
        values = []
        for element in (self.min_input, self.max_input):
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
            self.max_input.setCustomValidity("최대 면적은 최소 면적 이상이어야 합니다.")
            self.max_input.reportValidity()
            return None
        return (self.district_select.value, *values)

    def on_change(self, handler):
        """변경 알림 함수를 보관한다. 다시 연결해도 DOM 리스너는 중복하지 않는다."""
        self._change_handler = handler
        if self._listeners:
            return
        for element in (self.district_select, self.min_input, self.max_input):
            proxy = self._create_proxy(self._handle_change)
            element.addEventListener("change", proxy)
            self._listeners.append(proxy)

    def _handle_change(self, event):
        if self._change_handler is not None:
            self._change_handler()
