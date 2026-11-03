# 화면 4개 클래스 수정 완료 보고

2026-11-02 수정 계획서에 맞춰 MapDashboard가 맡던 일을 FilterPanel, MapView, ParkListView, Dashboard로 분리했습니다. 데이터 클래스 3개를 더하면 계획서의 총 7개 클래스가 됩니다.

## 변경한 책임

- FilterPanel: 구/면적 입력, 입력 검증, 변경 알림
- MapView: 지도, 마커 교체, Park 속성 기반 팝업, 선택 공원 이동
- ParkListView: 목록, 개수, 정렬 상태, Park 선택 알림
- Dashboard: 생성자로 받은 Manager와 화면 객체의 협력 흐름 조정

Dashboard는 js/DOM/Leaflet을 사용하지 않고, 화면 객체도 Dashboard를 import하지 않습니다. 팝업을 Park.get_popup_html()에 요청하던 계약은 MapView.make_popup(park)로 교체했습니다.

## 유지한 기능

5개 열, 구·면적 필터, 정렬 방향 전환, 마커/목록 동기 갱신, 빈 면적과 0 구분, 누락 좌표/면적/날짜 처리, 결과 0개, 반복 시작/갱신과 반복 클릭을 유지했습니다. 원본 데이터 읽기/정제/필터/정렬 알고리즘은 추가하지 않았습니다.

## 검증

단위 테스트 33개, 실제 PyScript 브라우저 테스트 22개가 통과했습니다. 별도 임시 폴더에서 팀원 코드와 실제 133개 공원을 연결해 확인했습니다. 상세 내용은 test-results.md를 참고하세요.

## 작업 범위

feature/map-dashboard의 기존 담당 파일과 그 대체 네 파일만 수정합니다. 바탕화면 검수 원본은 보존합니다. 루트 README, .gitignore, .nojekyll, 팀원의 main.py/HTML/CSS/설정/Park/DataLoader/ParkManager는 수정하지 않습니다. 기존 map_dashboard.py와 그 전용 단위 테스트 파일은 새 구조로 대체했고 Git 이력에서 이전 버전을 볼 수 있습니다.

사용자의 TXT 검수와 최종 확인을 거쳐 feature/map-dashboard 브랜치에 공유합니다. main 병합, PR 생성, Pages 설정 변경 및 배포는 이번 수정에 포함하지 않습니다.
