"""표준 라이브러리만 사용하는 CPython 단위 테스트. 브라우저 검증은 별도."""

import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from map_dashboard import MapDashboard


class Input:
    """면적 입력 검증에 필요한 최소 DOM 대역."""

    def __init__(self, value=""):
        self.value = value
        self.message = ""
        self.valid = True
        self.reported = False

    def setCustomValidity(self, message):
        self.message = message

    def checkValidity(self):
        return self.valid and not self.message

    def reportValidity(self):
        self.reported = True


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.manager = Mock()
        self.dashboard = MapDashboard(self.manager)
        self.dashboard._started = True
        self.dashboard._elements = {name: Input() for name in ("district", "min-area", "max-area")}
        self.dashboard._elements["park-count"] = SimpleNamespace(textContent="old")
        self.dashboard.draw_markers = Mock()
        self.dashboard.draw_list = Mock()
        self.filtered = [object(), object()]
        self.ordered = list(reversed(self.filtered))
        self.manager.filter.return_value = self.filtered
        self.manager.sort_by.return_value = self.ordered

    def test_constructor_only_stores_dependency_and_state(self):
        dashboard = MapDashboard(self.manager)
        self.assertIs(dashboard.manager, self.manager)
        self.assertEqual((dashboard.sort_key, dashboard.ascending), ("name", True))
        self.assertFalse(dashboard._started)
        self.manager.assert_not_called()

    def test_refresh_requires_start(self):
        with self.assertRaisesRegex(RuntimeError, "start"):
            MapDashboard(self.manager).refresh()

    def test_blank_bounds_pass_unchanged(self):
        self.dashboard.refresh()
        self.manager.filter.assert_called_once_with("", "", "")

    def test_delegates_same_filtered_list_in_correct_order(self):
        self.dashboard.refresh()
        self.assertEqual([call[0] for call in self.manager.method_calls], ["filter", "sort_by"])
        self.assertIs(self.manager.sort_by.call_args.args[0], self.filtered)
        self.manager.sort_by.assert_called_once_with(self.filtered, "name", True)

    def test_uses_manager_output_without_sorting_or_filtering_itself(self):
        # 필드조차 없는 객체도 Manager의 결과 순서 그대로 화면 계층에 전달한다.
        self.dashboard.refresh()
        self.dashboard.draw_markers.assert_called_once_with(self.ordered)
        self.dashboard.draw_list.assert_called_once_with(self.ordered)
        self.assertEqual(self.dashboard._elements["park-count"].textContent, "2")

    def test_render_then_count_update_order(self):
        trace = []
        self.manager.filter.side_effect = lambda *args: trace.append("filter") or self.filtered
        self.manager.sort_by.side_effect = lambda *args: trace.append("sort") or self.ordered
        self.dashboard.draw_markers.side_effect = lambda parks: trace.append("markers")
        self.dashboard.draw_list.side_effect = lambda parks: trace.append("list")
        self.dashboard.refresh()
        self.assertEqual(trace, ["filter", "sort", "markers", "list"])
        self.assertEqual(self.dashboard._elements["park-count"].textContent, "2")

    def test_numeric_bounds_and_district(self):
        self.dashboard._elements["district"].value = "종로구"
        self.dashboard._elements["min-area"].value = "12.5"
        self.dashboard._elements["max-area"].value = "2000"
        self.dashboard.refresh()
        self.manager.filter.assert_called_once_with("종로구", 12.5, 2000.0)

    def test_zero_is_not_blank(self):
        self.dashboard._elements["max-area"].value = "0"
        self.dashboard.refresh()
        self.manager.filter.assert_called_once_with("", "", 0.0)

    def test_min_only_and_max_only(self):
        for minimum, maximum, expected in [("10", "", (10.0, "")), ("", "10", ("", 10.0))]:
            with self.subTest(minimum=minimum, maximum=maximum):
                self.dashboard._elements["min-area"].value = minimum
                self.dashboard._elements["max-area"].value = maximum
                self.dashboard.refresh()
                self.assertEqual(self.manager.filter.call_args.args[1:], expected)

    def test_invalid_inputs_retain_previous_result(self):
        for value in ("oops", "-1", "nan", "inf", "-inf"):
            with self.subTest(value=value):
                self.dashboard._elements["min-area"].value = value
                self.dashboard.refresh()
                self.manager.filter.assert_not_called()
                self.assertEqual(self.dashboard._elements["park-count"].textContent, "old")
                self.assertTrue(self.dashboard._elements["min-area"].reported)

    def test_native_bad_input_does_not_become_blank(self):
        self.dashboard._elements["min-area"].valid = False
        self.dashboard.refresh()
        self.manager.filter.assert_not_called()

    def test_inverted_bounds_and_correction(self):
        self.dashboard._elements["min-area"].value = "20"
        self.dashboard._elements["max-area"].value = "10"
        self.dashboard.refresh()
        self.manager.filter.assert_not_called()
        self.dashboard._elements["max-area"].value = "30"
        self.dashboard.refresh()
        self.manager.filter.assert_called_once_with("", 20.0, 30.0)

    def test_empty_results_update_all_views(self):
        self.manager.filter.return_value = []
        self.manager.sort_by.return_value = []
        self.dashboard.refresh()
        self.dashboard.draw_markers.assert_called_once_with([])
        self.dashboard.draw_list.assert_called_once_with([])
        self.assertEqual(self.dashboard._elements["park-count"].textContent, "0")

    def test_sort_state_survives_filter_changes(self):
        self.dashboard.sort_key = "area"
        self.dashboard.ascending = False
        self.dashboard.on_filter_change()
        self.manager.sort_by.assert_called_once_with(self.filtered, "area", False)

    def test_header_switch_and_toggle(self):
        header = Mock()
        header.getAttribute.return_value = "area"
        self.dashboard._event_element = Mock(return_value=header)
        self.dashboard.on_header_click(object())
        self.assertEqual((self.dashboard.sort_key, self.dashboard.ascending), ("area", True))
        self.dashboard.on_header_click(object())
        self.assertEqual((self.dashboard.sort_key, self.dashboard.ascending), ("area", False))
        header.getAttribute.return_value = "department"
        self.dashboard.on_header_click(object())
        self.assertEqual((self.dashboard.sort_key, self.dashboard.ascending), ("department", True))

    def test_unknown_header_is_ignored(self):
        header = Mock()
        header.getAttribute.return_value = "not-a-column"
        self.dashboard._event_element = Mock(return_value=header)
        self.dashboard.on_header_click(object())
        self.manager.filter.assert_not_called()

    def test_no_event_is_harmless(self):
        self.dashboard.on_header_click()
        self.dashboard.on_row_click()
        self.manager.filter.assert_not_called()

    def test_missing_marker_does_not_move_map(self):
        row = Mock()
        row.getAttribute.return_value = "4"
        self.dashboard._event_element = Mock(return_value=row)
        self.dashboard._map = Mock()
        self.dashboard.on_row_click(object())
        self.dashboard._map.setView.assert_not_called()

    def test_repeated_row_clicks_reuse_marker(self):
        row = Mock()
        row.getAttribute.return_value = "0"
        self.dashboard._event_element = Mock(return_value=row)
        marker = Mock()
        self.dashboard._markers = {0: marker}
        self.dashboard._map = Mock()
        self.dashboard._js_options = lambda options: options
        for _ in range(3):
            self.dashboard.on_row_click(object())
        self.assertEqual(marker.openPopup.call_count, 3)
        self.assertEqual(self.dashboard._map.setView.call_count, 3)

    def test_valid_and_missing_coordinates(self):
        for location in (None, [], [None, None], ["", 127], [37], [1, 2, 3], [91, 0], [0, 181], [float("nan"), 127], [37, float("inf")]):
            with self.subTest(location=location):
                self.assertIsNone(MapDashboard._valid_location(location))
        self.assertEqual(MapDashboard._valid_location([0, 0]), [0.0, 0.0])
        self.assertEqual(MapDashboard._valid_location([37.5, 127]), [37.5, 127.0])

    def test_missing_and_zero_display_values(self):
        self.assertEqual(self.dashboard._label(None), "정보 없음")
        self.assertEqual(self.dashboard._label(""), "정보 없음")
        self.assertEqual(self.dashboard._label(0), "0")
        self.assertEqual(self.dashboard._area_label(SimpleNamespace(area=0)), "0 ㎡")
        self.assertEqual(self.dashboard._area_label(SimpleNamespace(area=None)), "정보 없음")
        self.assertEqual(self.dashboard._area_label(SimpleNamespace(area=100, area_text="표시용 면적")), "표시용 면적")

    def test_start_is_idempotent(self):
        self.dashboard.start()
        self.manager.get_districts.assert_not_called()

    def test_missing_html_ids_fail_before_leaflet_creation(self):
        document = Mock()
        document.getElementById.return_value = None
        leaflet = Mock()
        modules = {
            "js": SimpleNamespace(document=document, L=leaflet, Object=Mock()),
            "pyodide": SimpleNamespace(),
            "pyodide.ffi": SimpleNamespace(create_proxy=Mock(), to_js=Mock()),
        }
        with patch.dict(sys.modules, modules):
            with self.assertRaisesRegex(ValueError, "park-list"):
                MapDashboard(self.manager).start()
        leaflet.map.assert_not_called()


if __name__ == "__main__":
    unittest.main()
