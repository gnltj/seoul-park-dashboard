"""입력 계약, 팝업 생성, 선택/정렬 알림의 단위 테스트. DOM은 브라우저에서 별도 검증."""

from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from filter_panel import FilterPanel
from map_view import MapView
from park_list_view import ParkListView


class Input:
    def __init__(self, value=""):
        self.value = value
        self.message = ""
        self.valid = True
        self.reported = False

    def setCustomValidity(self, value):
        self.message = value

    def checkValidity(self):
        return self.valid and not self.message

    def reportValidity(self):
        self.reported = True


class FilterPanelTests(unittest.TestCase):
    def setUp(self):
        self.panel = FilterPanel.__new__(FilterPanel)
        self.panel.district_select = Input()
        self.panel.min_input = Input()
        self.panel.max_input = Input()

    def test_empty_bounds_preserved(self):
        self.assertEqual(self.panel.get_values(), ("", "", ""))

    def test_zero_and_decimal_are_numbers(self):
        self.panel.district_select.value = "종로구"
        self.panel.min_input.value = "0"
        self.panel.max_input.value = "12.5"
        self.assertEqual(self.panel.get_values(), ("종로구", 0.0, 12.5))

    def test_one_sided_bounds(self):
        for minimum, maximum, expected in [("1", "", (1.0, "")), ("", "1", ("", 1.0))]:
            with self.subTest(minimum=minimum, maximum=maximum):
                self.panel.min_input.value, self.panel.max_input.value = minimum, maximum
                self.assertEqual(self.panel.get_values()[1:], expected)

    def test_bad_numbers_rejected(self):
        for value in ("oops", "-1", "nan", "inf", "-inf"):
            with self.subTest(value=value):
                self.panel.min_input.value = value
                self.assertIsNone(self.panel.get_values())
                self.assertTrue(self.panel.min_input.reported)

    def test_native_bad_input_is_not_unset_condition(self):
        self.panel.min_input.valid = False
        self.assertIsNone(self.panel.get_values())

    def test_inverted_bounds_and_recovery(self):
        self.panel.min_input.value, self.panel.max_input.value = "20", "10"
        self.assertIsNone(self.panel.get_values())
        self.panel.max_input.value = "30"
        self.assertEqual(self.panel.get_values(), ("", 20.0, 30.0))

    def test_rebinding_changes_handler_without_duplicate_listeners(self):
        elements = [Mock(), Mock(), Mock()]
        self.panel.district_select, self.panel.min_input, self.panel.max_input = elements
        self.panel._listeners = []
        self.panel._create_proxy = lambda handler: handler
        first, second = Mock(), Mock()
        self.panel.on_change(first)
        self.panel.on_change(second)
        for element in elements:
            element.addEventListener.assert_called_once()
        self.panel._handle_change(object())
        first.assert_not_called()
        second.assert_called_once_with()


class MapViewTests(unittest.TestCase):
    def setUp(self):
        self.view = MapView.__new__(MapView)

    def test_missing_and_invalid_coordinates(self):
        for value in (None, [], [None, None], ["", 127], [37], [1, 2, 3], [91, 0], [0, 181], [float("nan"), 127], [37, float("inf")]):
            with self.subTest(value=value):
                self.assertIsNone(self.view._valid_location(value))

    def test_zero_and_regular_coordinates_valid(self):
        self.assertEqual(self.view._valid_location([0, 0]), [0.0, 0.0])
        self.assertEqual(self.view._valid_location([37.5, 127]), [37.5, 127.0])

    def test_popup_does_not_require_park_popup_method(self):
        park = SimpleNamespace(name="공원", area=0, department="부서")
        popup = self.view.make_popup(park)
        self.assertIn("공원", popup)
        self.assertIn("0 ㎡", popup)
        self.assertIn("전화번호: </div>", popup)
        self.assertNotIn("정보 없음", popup)

    def test_popup_escapes_text(self):
        popup = self.view.make_popup(SimpleNamespace(name='<img src=x onerror="alert(1)">', area=None))
        self.assertNotIn("<img", popup)
        self.assertIn("&lt;img", popup)

    def test_popup_links_are_links_and_http_only(self):
        park = SimpleNamespace(name="공원", guide_map='https://example.com/?q="a"', image="http://example.com/image", link="javascript:alert(1)")
        popup = self.view.make_popup(park)
        self.assertEqual(popup.count("<a "), 2)
        self.assertNotIn("<img", popup)
        self.assertNotIn("javascript:", popup)
        self.assertIn("&quot;a&quot;", popup)
        self.assertIn('rel="noopener noreferrer"', popup)

    def test_invalid_link_forms_are_blank(self):
        for value in (None, "", "/relative", "data:text/html,x", "ftp://example.com", "https://[bad"):
            with self.subTest(value=value):
                self.assertEqual(self.view._safe_url(value), "")

    def test_focus_reuses_selected_object_marker(self):
        park = SimpleNamespace(get_location=lambda: [37.5, 127])
        marker = Mock()
        self.view.markers = {id(park): marker}
        self.view.map = Mock()
        self.view._to_js = lambda value: value
        self.view._js_options = lambda value: value
        for _ in range(3):
            self.view.focus(park)
        self.assertEqual(marker.openPopup.call_count, 3)
        self.view.map.setView.assert_called_with([37.5, 127.0], 15, {"animate": False})

    def test_missing_location_does_not_move_map(self):
        self.view.map = Mock()
        self.view.markers = {}
        self.view.focus(SimpleNamespace(get_location=lambda: [None, None]))
        self.view.map.setView.assert_not_called()


class ParkListViewTests(unittest.TestCase):
    def setUp(self):
        self.view = ParkListView.__new__(ParkListView)
        self.view.sort_key, self.view.ascending = "name", True
        self.view._event_element = Mock()
        self.view._update_headers = Mock()
        self.view._sort_handler = Mock()

    def test_default_sort(self):
        self.assertEqual(self.view.get_sort(), ("name", True))

    def test_same_header_toggles_then_other_starts_ascending(self):
        header = Mock()
        self.view._event_element.return_value = header
        header.getAttribute.return_value = "name"
        self.view._handle_header_click(object())
        self.assertEqual(self.view.get_sort(), ("name", False))
        header.getAttribute.return_value = "area"
        self.view._handle_header_click(object())
        self.assertEqual(self.view.get_sort(), ("area", True))

    def test_sort_state_is_updated_before_callback(self):
        self.view._event_element.return_value.getAttribute.return_value = "area"
        observed = []
        self.view._sort_handler = lambda: observed.append(self.view.get_sort())
        self.view._handle_header_click(object())
        self.assertEqual(observed, [("area", True)])

    def test_unknown_header_is_ignored(self):
        self.view._event_element.return_value.getAttribute.return_value = "unknown"
        self.view._handle_header_click(object())
        self.view._sort_handler.assert_not_called()

    def test_selected_row_delivers_park_not_index(self):
        parks = [object(), object()]
        self.view.shown_parks = parks
        self.view._select_handler = Mock()
        self.view._event_element.return_value.getAttribute.return_value = "1"
        self.view._handle_row_click(object())
        self.view._select_handler.assert_called_once_with(parks[1])

    def test_missing_and_zero_labels(self):
        self.assertEqual(self.view._label(None), "정보 없음")
        self.assertEqual(self.view._area_label(SimpleNamespace(area=None)), "정보 없음")
        self.assertEqual(self.view._area_label(SimpleNamespace(area=0)), "0 ㎡")
        self.assertEqual(self.view._area_label(SimpleNamespace(area=100, area_text="표시용")), "표시용")


if __name__ == "__main__":
    unittest.main()
