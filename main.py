"""시작 파일 (클래스 아님).

Park를 뺀 여섯 클래스의 객체를 만들고 서로 연결한다.
Park 객체는 DataLoader가 만든다.
"""

from data_loader import DataLoader
from park_manager import ParkManager
from filter_panel import FilterPanel
from map_view import MapView
from park_list_view import ParkListView
from dashboard import Dashboard

CSV_PATH = "parks.csv"


def main():
    """객체를 만들어 연결하고 대시보드를 시작한다."""
    parks = DataLoader(CSV_PATH).load()                                       # 1~2단계
    manager = ParkManager(parks)                                              # 3단계
    dashboard = Dashboard(manager, FilterPanel(), MapView(), ParkListView())  # 4단계
    dashboard.start()                                                         # 5~6단계
    return dashboard


# 페이지가 열려 있는 동안 dashboard 객체가 사라지지 않도록 전역 변수에 저장
dashboard = main()