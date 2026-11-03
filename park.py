"""공원 한 곳의 정보를 담는 Park 클래스."""

class Park:
    """공원 한 곳의 정보를 담고, 위치와 정렬에 쓸 값을 돌려준다.

    값 정리(빈칸, 면적 숫자 변환 등)는 DataLoader가 맡고,
    Park는 정리된 값을 받아 보관만 한다. Park는 다른 클래스를 부르지 않는다.
    """

    SORT_ATTRS = {
        "name": "name",
        "district": "district",
        "area": "area",
        "open_date": "open_date_value",
        "department": "department",
    }

    def __init__(self, data):
        """DataLoader가 정리한 dict로 객체를 만든다.

        엑셀 18개 항목(GRS80TM 좌표 제외)과 면적 숫자 area,
        개원일 숫자 리스트 open_date_value를 키로 받는다.
        없는 키는 None으로 둔다.
        """
        self.id = data.get("id")                    # 연번
        self.name = data.get("name")                # 공원명
        self.summary = data.get("summary")          # 공원개요
        self.area_text = data.get("area_text")      # 면적 (엑셀 원문)
        self.area = data.get("area")                # 면적 숫자 (to_number 결과)
        self.open_date = data.get("open_date")      # 개원일
        self.open_date_value = data.get("open_date_value")  # 개원일 숫자 리스트 (to_date_value 결과)
        self.facilities = data.get("facilities")    # 주요시설
        self.plants = data.get("plants")            # 주요식물
        self.guide_map = data.get("guide_map")      # 안내도 링크
        self.directions = data.get("directions")    # 오시는길
        self.notes = data.get("notes")              # 이용시 참고사항
        self.image = data.get("image")              # 이미지 링크
        self.district = data.get("district")        # 지역(구)
        self.address = data.get("address")          # 공원주소
        self.department = data.get("department")    # 관리부서
        self.phone = data.get("phone")              # 전화번호
        self.lng = data.get("lng")                  # X좌표(WGS84) = 경도
        self.lat = data.get("lat")                  # Y좌표(WGS84) = 위도
        self.link = data.get("link")                # 바로가기 링크

    def get_location(self):
        """[위도, 경도]를 반환한다. 좌표가 없으면 해당 값은 None이다."""
        return [self.lat, self.lng]

    def get_sort_value(self, key):
        """SORT_ATTRS 표에서 비교할 속성을 찾아 값을 반환한다. 값이 없으면 None."""
        value = getattr(self, self.SORT_ATTRS[key])
        if value == "":
            return None
        return value