"""표준 라이브러리로 독립 데모를 로컬에서 실행한다. 팀 통합에는 불필요하다."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import webbrowser


def main():
    parser = argparse.ArgumentParser(description="MapDashboard 독립 데모 실행")
    parser.add_argument("--port", type=int, default=8765, help="로컬 서버 포트 (기본 8765)")
    parser.add_argument("--test", action="store_true", help="브라우저 통합 테스트 실행")
    parser.add_argument("--no-browser", action="store_true", help="브라우저를 자동으로 열지 않음")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    handler = partial(SimpleHTTPRequestHandler, directory=str(root))
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    except OSError as error:
        print(f"서버를 시작할 수 없습니다: {error}")
        print("이미 실행 중인 서버를 종료하거나 --port 8766으로 다시 실행하세요.")
        return 1
    url = f"http://127.0.0.1:{args.port}/demo/index.html" + ("?test=1" if args.test else "")
    print(f"MapDashboard: {url}", flush=True)
    print("종료하려면 이 창에서 Ctrl+C를 누르세요.", flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
