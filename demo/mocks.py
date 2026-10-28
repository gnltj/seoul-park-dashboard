"""테스트용 최소 구현. 실제 Park/ParkManager 또는 실제 공원 데이터가 아니다."""

from dataclasses import dataclass
from html import escape


@dataclass
class MockPark:
    id: str
    name: str
    district: str
    area: float | None
    lat: float | None
    lng: float | None
    open_date: str | None = None
    department: str = "가상 관리부서"
    area_text: str | None = None
    address: str = "시연용 가상 주소"

    def get_location(self):
        return [self.lat, self.lng]

    def get_popup_html(self):
        # HTML을 제공하는 객체가 원본 텍스트를 escape하는 계약을 시연한다.
        area = self.area_text if self.area_text else ("정보 없음" if self.area is None else f"{self.area:,} ㎡")
        return (
            f"<strong>{escape(self.name)}</strong><br>"
            f"지역: {escape(self.district)}<br>면적: {escape(area)}<br>"
            f"개원일: {escape(self.open_date or '정보 없음')}<br>"
            f"관리부서: {escape(self.department)}<br>주소: {escape(self.address)}"
        )

    def get_sort_value(self, key):
        return getattr(self, key)


class MockParkManager:
    """샘플 데이터 검증에만 쓰는 필터/정렬과 호출 기록."""

    def __init__(self, parks):
        self.parks = list(parks)
        self.calls = []

    def get_districts(self):
        self.calls.append(("get_districts",))
        return sorted({park.district for park in self.parks})

    def filter(self, district, min_area, max_area):
        self.calls.append(("filter", district, min_area, max_area))
        result = []
        for park in self.parks:
            if district and park.district != district:
                continue
            if min_area not in ("", None) and (park.area is None or park.area < min_area):
                continue
            if max_area not in ("", None) and (park.area is None or park.area > max_area):
                continue
            result.append(park)
        return result

    def sort_by(self, parks, key, ascending):
        self.calls.append(("sort_by", key, ascending))
        # 결측값 정책은 Manager 책임이다. 모의 구현은 항상 결측값을 마지막에 둔다.
        present = [park for park in parks if park.get_sort_value(key) is not None]
        missing = [park for park in parks if park.get_sort_value(key) is None]
        return sorted(present, key=lambda park: park.get_sort_value(key), reverse=not ascending) + missing


def sample_parks():
    """가상 공원 6개: 좌표 없음, 면적 없음, 개원일 없음, 실제 0 면적 포함."""
    return [
        MockPark("demo-1", "가람공원 (가상)", "강남구", 1000, 37.4979, 127.0276, "2000-05-01", "가상 A부서", "1,000 ㎡"),
        MockPark("demo-2", "나래공원 (가상)", "종로구", 5000, 37.5735, 126.9790, None, "가상 B부서"),
        MockPark("demo-3", "다온공원 (가상)", "마포구", None, 37.5663, 126.9019, "2010-03-01"),
        MockPark("demo-4", "라온공원 (가상)", "종로구", 0, 37.5830, 126.9900, None),
        MockPark("demo-5", "마루공원 (가상)", "강남구", 2000, None, None, "2015-10-01"),
        MockPark("demo-6", "바른공원 (가상)", "성동구", 3000, 37.5445, 127.0374, "2005-06-01"),
    ]
