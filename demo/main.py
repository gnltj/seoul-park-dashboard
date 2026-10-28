"""팀 통합 시 실제 Manager를 연결하는 진입 코드로 교체할 파일."""

from js import document, window

from map_dashboard import MapDashboard
from mocks import MockParkManager, sample_parks


try:
    manager = MockParkManager(sample_parks())
    dashboard = MapDashboard(manager)
    dashboard.start()
    document.getElementById("demo-status").textContent = "준비 완료 · 가상 데이터 6개"
    if window.location.search == "?test=1":
        from browser_checks import run_checks
        run_checks(dashboard, manager)
except Exception as error:
    document.getElementById("demo-status").textContent = f"실행 오류: {error}"
    raise
