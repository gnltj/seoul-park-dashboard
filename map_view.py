"""Leaflet 지도·마커·팝업과 선택 공원으로의 이동을 담당한다."""

from html import escape
from math import isfinite
from urllib.parse import urlsplit


class MapView:
    SEOUL_CENTER = (37.5665, 126.9780)

    def __init__(self):
        from js import L, Object, document
        from pyodide.ffi import to_js

        element = document.getElementById("map")
        if element is None:
            raise ValueError("필수 HTML ID가 없습니다: map")
        self._leaflet = L
        self._object = Object
        self._to_js = to_js
        self.map = L.map(element).setView(to_js(list(self.SEOUL_CENTER)), 11)
        L.tileLayer(
            "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            self._js_options({
                "maxZoom": 19,
                "attribution": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            }),
        ).addTo(self.map)
        self.marker_layer = L.layerGroup().addTo(self.map)
        self.markers = {}

    def show(self, parks):
        """마커를 교체한다. 좌표 없는 공원은 목록 결과를 바꾸지 않고 건너뛴다."""
        self.marker_layer.clearLayers()
        self.markers.clear()
        for park in parks:
            location = self._valid_location(park.get_location())
            if location is None:
                continue
            marker = self._leaflet.marker(self._to_js(location))
            # 실제 공원의 긴 설명은 팝업 안에서 스크롤해 지도 밖으로 넘치지 않게 한다.
            marker.bindPopup(self.make_popup(park), self._js_options({"maxHeight": 300})).addTo(self.marker_layer)
            # Park가 dataclass이거나 id가 중복돼도 실제 선택 객체와 연결한다.
            self.markers[id(park)] = marker

    def make_popup(self, park):
        """Park의 속성으로 팝업 HTML을 만든다. 누락된 값은 빈칸으로 표시한다."""
        name = self._text(getattr(park, "name", None))
        area = getattr(park, "area_text", None)
        if area is None or area == "":
            number = getattr(park, "area", None)
            area = "" if number is None else f"{number:,} ㎡"
        fields = [
            ("지역", getattr(park, "district", None)),
            ("주소", getattr(park, "address", None)),
            ("면적", area),
            ("개원일", getattr(park, "open_date", None)),
            ("관리부서", getattr(park, "department", None)),
            ("전화번호", getattr(park, "phone", None)),
            ("주요시설", getattr(park, "facilities", None)),
            ("주요식물", getattr(park, "plants", None)),
            ("공원개요", getattr(park, "summary", None)),
            ("오시는길", getattr(park, "directions", None)),
            ("참고사항", getattr(park, "notes", None)),
        ]
        parts = [f"<strong>{name}</strong>"]
        parts.extend(f"<div>{label}: {self._text(value)}</div>" for label, value in fields)
        for key, label in (("guide_map", "안내도"), ("image", "이미지"), ("link", "바로가기")):
            url = self._safe_url(getattr(park, key, None))
            value = f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{label} 열기</a>' if url else ""
            parts.append(f"<div>{label}: {value}</div>")
        return "".join(parts)

    def focus(self, park):
        """선택한 공원의 위치로 즉시 이동하고 그 마커의 팝업을 연다."""
        location = self._valid_location(park.get_location())
        marker = self.markers.get(id(park))
        if location is None or marker is None:
            return
        self.map.setView(self._to_js(location), 15, self._js_options({"animate": False}))
        marker.openPopup()

    def _js_options(self, options):
        return self._to_js(options, dict_converter=self._object.fromEntries)

    @staticmethod
    def _text(value):
        return "" if value is None else escape(str(value))

    @staticmethod
    def _safe_url(value):
        if not value:
            return ""
        text = str(value).strip()
        try:
            parsed = urlsplit(text)
            return text if parsed.scheme.lower() in ("http", "https") and parsed.netloc else ""
        except ValueError:
            return ""

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
