"""브라우저 없이 협력 객체만으로 Dashboard의 흐름을 검증한다."""

import ast
from pathlib import Path
import unittest
from unittest.mock import Mock

from dashboard import Dashboard


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.manager = Mock()
        self.panel = Mock()
        self.map_view = Mock()
        self.list_view = Mock()
        self.panel.get_values.return_value = ("", "", "")
        self.list_view.get_sort.return_value = ("name", True)
        self.filtered = [object(), object()]
        self.ordered = list(reversed(self.filtered))
        self.manager.get_districts.return_value = ["강남구", "종로구"]
        self.manager.filter.return_value = self.filtered
        self.manager.sort_by.return_value = self.ordered
        self.dashboard = Dashboard(self.manager, self.panel, self.map_view, self.list_view)

    def test_constructor_stores_injected_objects(self):
        self.assertIs(self.dashboard.manager, self.manager)
        self.assertIs(self.dashboard.filter_panel, self.panel)
        self.assertIs(self.dashboard.map_view, self.map_view)
        self.assertIs(self.dashboard.list_view, self.list_view)
        self.assertFalse(self.dashboard._started)

    def test_start_fills_options_and_connects_callbacks(self):
        self.dashboard.start()
        self.panel.fill_districts.assert_called_once_with(["강남구", "종로구"])
        self.panel.on_change.assert_called_once_with(self.dashboard.refresh)
        self.list_view.on_sort_change.assert_called_once_with(self.dashboard.refresh)
        self.list_view.on_select.assert_called_once_with(self.dashboard.on_park_selected)

    def test_start_is_idempotent(self):
        self.dashboard.start()
        self.dashboard.start()
        self.manager.get_districts.assert_called_once()
        self.panel.on_change.assert_called_once()
        self.manager.filter.assert_called_once()

    def test_refresh_requires_start(self):
        with self.assertRaisesRegex(RuntimeError, "start"):
            self.dashboard.refresh()

    def test_blank_bounds_are_not_zero(self):
        self.dashboard.start()
        self.manager.filter.assert_called_once_with("", "", "")

    def test_reads_conditions_and_sort_from_views(self):
        self.panel.get_values.return_value = ("종로구", "", 0.0)
        self.list_view.get_sort.return_value = ("area", False)
        self.dashboard.start()
        self.manager.filter.assert_called_once_with("종로구", "", 0.0)
        self.manager.sort_by.assert_called_once_with(self.filtered, "area", False)

    def test_delegation_and_render_order(self):
        calls = Mock()
        for name, obj in (("panel", self.panel), ("list_view", self.list_view), ("manager", self.manager), ("map_view", self.map_view)):
            calls.attach_mock(obj, name)
        self.dashboard.start()
        names = [call[0] for call in calls.mock_calls]
        expected = ["panel.get_values", "list_view.get_sort", "manager.filter", "manager.sort_by", "map_view.show", "list_view.show"]
        self.assertEqual(names[-6:], expected)
        self.assertIs(self.manager.sort_by.call_args.args[0], self.filtered)
        self.map_view.show.assert_called_once_with(self.ordered)
        self.list_view.show.assert_called_once_with(self.ordered)

    def test_invalid_filters_keep_existing_views(self):
        self.panel.get_values.return_value = None
        self.dashboard.start()
        self.manager.filter.assert_not_called()
        self.list_view.get_sort.assert_not_called()
        self.map_view.show.assert_not_called()
        self.list_view.show.assert_not_called()

    def test_empty_results_reach_both_views(self):
        self.manager.filter.return_value = []
        self.manager.sort_by.return_value = []
        self.dashboard.start()
        self.map_view.show.assert_called_once_with([])
        self.list_view.show.assert_called_once_with([])

    def test_generator_result_is_materialized_for_both_views(self):
        self.manager.sort_by.return_value = iter(self.ordered)
        self.dashboard.start()
        self.map_view.show.assert_called_once_with(self.ordered)
        self.list_view.show.assert_called_once_with(self.ordered)

    def test_row_selection_forwards_exact_park(self):
        park = object()
        self.dashboard.on_park_selected(park)
        self.map_view.focus.assert_called_once_with(park)

    def test_no_browser_imports_in_controller(self):
        tree = ast.parse((Path(__file__).parents[1] / "dashboard.py").read_text(encoding="utf-8"))
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        self.assertEqual(imports, [])


if __name__ == "__main__":
    unittest.main()
