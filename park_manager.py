import math


class ParkManager:
    ALL_DISTRICTS = "전체"

    def __init__(self, parks):
        self.parks = list(parks)

    def get_districts(self):
        return sorted({park.district for park in self.parks if park.district})

    def filter(self, district=None, min_area=None, max_area=None):
        min_area = self._to_limit(min_area)
        max_area = self._to_limit(max_area)

        result = []
        for park in self.parks:
            if not self._match_district(park, district):
                continue
            if not self._match_area(park, min_area, max_area):
                continue
            result.append(park)
        return result

    def sort_by(self, parks, key, ascending=True):
        with_value = []
        without_value = []
        for park in parks:
            value = park.get_sort_value(key)
            if value is None:
                without_value.append(park)
            else:
                with_value.append((value, park))

        with_value.sort(key=lambda pair: pair[0], reverse=not ascending)
        return [park for _, park in with_value] + without_value

    def _match_district(self, park, district):
        if district in (None, "", self.ALL_DISTRICTS):
            return True
        return park.district == district

    def _match_area(self, park, min_area, max_area):
        if min_area is None and max_area is None:
            return True
        if park.area is None:
            return False
        if min_area is not None and park.area < min_area:
            return False
        if max_area is not None and park.area > max_area:
            return False
        return True

    @staticmethod
    def _to_limit(value):
        if value is None:
            return None
        text = str(value).strip()
        if text == "":
            return None
        try:
            number = float(text)
        except ValueError:
            return None
        if not math.isfinite(number):
            return None
        return number
