"""데이터 관리자와 화면 객체들을 연결한다. 브라우저에는 직접 접근하지 않는다."""


class Dashboard:
    def __init__(self, manager, filter_panel, map_view, list_view):
        """함께 일할 객체를 main.py 또는 테스트 진입 코드에서 전달받는다."""
        self.manager = manager
        self.filter_panel = filter_panel
        self.map_view = map_view
        self.list_view = list_view
        self._started = False

    def start(self):
        """구 목록을 채우고 화면의 알림을 연결한 뒤 처음 갱신한다."""
        if self._started:
            return
        self.filter_panel.fill_districts(self.manager.get_districts())
        self.filter_panel.on_change(self.refresh)
        self.list_view.on_sort_change(self.refresh)
        self.list_view.on_select(self.on_park_selected)
        self._started = True
        self.refresh()

    def refresh(self):
        """조건/정렬 기준 읽기 → 처리 위임 → 지도와 목록 표시 순서로 진행한다."""
        if not self._started:
            raise RuntimeError("start()를 먼저 호출하세요.")
        values = self.filter_panel.get_values()
        if values is None:
            return
        key, ascending = self.list_view.get_sort()
        filtered = self.manager.filter(*values)
        parks = list(self.manager.sort_by(filtered, key, ascending))
        self.map_view.show(parks)
        self.list_view.show(parks)

    def on_park_selected(self, park):
        """목록이 알려 준 공원 객체를 지도에 그대로 전달한다."""
        self.map_view.focus(park)
