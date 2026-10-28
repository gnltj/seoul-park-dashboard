"""?test=1에서 실제 PyScript/DOM/Leaflet으로 실행하는 통합 테스트."""

import io
import unittest

from js import Event, document


def run_checks(dashboard, manager):
    class BrowserTests(unittest.TestCase):
        def setUp(self):
            for name in ("district", "min-area", "max-area"):
                document.getElementById(name).value = ""
            dashboard.sort_key = "name"
            dashboard.ascending = True
            dashboard.refresh()
            manager.calls.clear()

        def change(self, name, value):
            element = document.getElementById(name)
            element.value = value
            element.dispatchEvent(Event.new("change"))

        def header(self, key):
            document.querySelector(f'[data-sort-key="{key}"]').click()

        def test_01_map_and_center(self):
            self.assertEqual(document.querySelectorAll(".leaflet-container").length, 1)
            self.assertTrue(dashboard._map.dragging.enabled())
            self.assertTrue(dashboard._map.scrollWheelZoom.enabled())

        def test_02_rows_columns_and_count(self):
            self.assertEqual(document.querySelectorAll("[data-park-index]").length, 6)
            self.assertEqual(document.querySelectorAll("#park-list th").length, 5)
            self.assertEqual(document.getElementById("park-count").textContent, "6")

        def test_03_marker_positions(self):
            self.assertEqual(dashboard._marker_layer.getLayers().length, 5)
            marker = dashboard._markers[0]
            self.assertAlmostEqual(marker.getLatLng().lat, 37.4979)
            self.assertAlmostEqual(marker.getLatLng().lng, 127.0276)

        def test_04_marker_click_popup(self):
            marker = dashboard._markers[0]
            marker.getElement().click()
            self.assertTrue(marker.isPopupOpen())
            self.assertIn("가람공원", document.querySelector(".leaflet-popup-content").textContent)

        def test_05_row_click_and_repeat(self):
            row_button = document.querySelector('[data-park-index="1"] button')
            for _ in range(3):
                row_button.click()
                self.assertTrue(dashboard._markers[1].isPopupOpen())
            # 팝업 자동 패닝으로 중심이 보정될 수 있으므로 마커가 보이는지 확인한다.
            self.assertTrue(dashboard._map.getBounds().contains(dashboard._markers[1].getLatLng()))
            self.assertEqual(dashboard._map.getZoom(), 15)

        def test_06_district_change(self):
            self.change("district", "강남구")
            self.assertEqual([park.id for park in dashboard.parks], ["demo-1", "demo-5"])
            self.assertEqual(document.getElementById("park-count").textContent, "2")
            self.assertEqual(dashboard._marker_layer.getLayers().length, 1)

        def test_07_minimum_change(self):
            self.change("min-area", "2000")
            self.assertEqual([park.id for park in dashboard.parks], ["demo-2", "demo-5", "demo-6"])
            self.assertEqual(manager.calls[0], ("filter", "", 2000.0, ""))

        def test_08_maximum_change(self):
            self.change("max-area", "1000")
            self.assertEqual([park.id for park in dashboard.parks], ["demo-1", "demo-4"])

        def test_09_blank_and_zero_are_distinct(self):
            dashboard.refresh()
            self.assertEqual(manager.calls[0], ("filter", "", "", ""))
            self.change("max-area", "0")
            self.assertEqual([park.id for park in dashboard.parks], ["demo-4"])
            self.assertIn(("filter", "", "", 0.0), manager.calls)

        def test_10_all_headers_toggle(self):
            for key, _ in dashboard.COLUMNS:
                previous = dashboard.ascending if dashboard.sort_key == key else False
                self.header(key)
                self.assertEqual(dashboard.sort_key, key)
                self.assertEqual(dashboard.ascending, not previous)
                self.header(key)
                self.assertEqual(dashboard.ascending, previous)
                self.assertEqual(manager.calls[-1], ("sort_by", key, previous))

        def test_11_numeric_order(self):
            self.header("area")
            self.assertEqual([park.id for park in dashboard.parks], ["demo-4", "demo-1", "demo-5", "demo-6", "demo-2", "demo-3"])
            self.header("area")
            self.assertEqual([park.id for park in dashboard.parks], ["demo-2", "demo-6", "demo-5", "demo-1", "demo-4", "demo-3"])

        def test_12_missing_values(self):
            self.assertIn("정보 없음", document.querySelector('[data-park-index="2"]').textContent)
            self.assertIn("정보 없음", document.querySelector('[data-park-index="1"]').textContent)
            self.assertIn("0 ㎡", document.querySelector('[data-park-index="3"]').textContent)

        def test_13_missing_location_row(self):
            document.querySelector('[data-park-index="4"] button').click()
            self.assertNotIn(4, dashboard._markers)
            self.assertEqual(document.getElementById("park-count").textContent, "6")

        def test_14_empty_results_and_recovery(self):
            self.change("min-area", "9999999")
            self.assertEqual(document.getElementById("park-count").textContent, "0")
            self.assertEqual(dashboard._marker_layer.getLayers().length, 0)
            self.assertEqual(document.querySelectorAll("[data-park-index]").length, 0)
            self.assertIn("조건에 맞는 공원이 없습니다", document.getElementById("park-list").textContent)
            self.change("min-area", "")
            self.assertEqual(len(dashboard.parks), 6)

        def test_15_repeated_refresh_and_start(self):
            for _ in range(20):
                dashboard.start()
                dashboard.refresh()
            self.assertEqual(len(dashboard._listeners), 5)
            self.assertEqual(dashboard._marker_layer.getLayers().length, 5)
            self.assertEqual(document.querySelectorAll(".leaflet-marker-icon").length, 5)
            self.assertEqual(document.querySelectorAll("#district option").length, 5)
            manager.calls.clear()
            self.change("district", "종로구")
            self.assertEqual(manager.calls, [("filter", "종로구", "", ""), ("sort_by", "name", True)])

        def test_16_rapid_changes(self):
            for district, count in [("강남구", 2), ("마포구", 1), ("성동구", 1), ("", 6)] * 5:
                self.change("district", district)
                self.assertEqual(document.getElementById("park-count").textContent, str(count))

        def test_17_sort_then_click_uses_current_row(self):
            self.header("area")
            document.querySelector('[data-park-index="0"] button').click()
            self.assertTrue(dashboard._markers[0].isPopupOpen())
            popup = dashboard._markers[0].getPopup().getElement()
            self.assertIn("라온공원", popup.querySelector(".leaflet-popup-content").textContent)

        def test_18_filter_keeps_sort(self):
            self.header("area")
            self.header("area")
            self.change("district", "종로구")
            self.assertEqual([park.id for park in dashboard.parks], ["demo-2", "demo-4"])
            self.assertFalse(dashboard.ascending)

        def test_19_text_is_not_interpreted_as_html(self):
            park = manager.parks[0]
            original = park.name
            try:
                park.name = '<img src=x onerror="alert(1)">'
                dashboard.refresh()
                self.assertEqual(document.querySelectorAll("#park-list img").length, 0)
                self.assertIn("<img", document.getElementById("park-list").textContent)
            finally:
                park.name = original

        def test_20_filter_then_sort_delegation(self):
            self.change("min-area", "1000.5")
            self.assertEqual(manager.calls, [("filter", "", 1000.5, ""), ("sort_by", "name", True)])

        def test_21_list_container_div(self):
            original = dashboard._elements["park-list"]
            temporary = document.createElement("div")
            dashboard._elements["park-list"] = temporary
            try:
                dashboard.draw_list(dashboard.parks)
                self.assertEqual(temporary.querySelectorAll("table").length, 1)
                self.assertEqual(temporary.querySelectorAll("td").length, 30)
            finally:
                dashboard._elements["park-list"] = original

        def test_22_event_delegation_after_redraw(self):
            for _ in range(4):
                self.header("name")
            self.assertTrue(dashboard.ascending)
            self.assertEqual(len([call for call in manager.calls if call[0] == "sort_by"]), 4)

    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(BrowserTests)
    )
    # 통합 테스트 후 일반 데모 상태로 복구한다.
    for name in ("district", "min-area", "max-area"):
        document.getElementById(name).value = ""
    dashboard.sort_key = "name"
    dashboard.ascending = True
    dashboard.refresh()
    dashboard._map.setView(dashboard._to_js(list(dashboard.SEOUL_CENTER)), 11)
    panel = document.getElementById("test-results")
    panel.hidden = False
    panel.textContent = output.getvalue()
    panel.setAttribute("data-result", "pass" if result.wasSuccessful() else "fail")
    document.getElementById("demo-status").textContent = (
        f"브라우저 통합 테스트: {result.testsRun}개 / 실패 {len(result.failures)} / 오류 {len(result.errors)}"
    )
