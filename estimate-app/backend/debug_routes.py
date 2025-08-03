from app.main import app

def main():
    # APIドキュメント生成に関係なく、全 route を出力
    for route in app.routes:
        # Starlette/FastAPI の BaseRoute としてインポートせずに安全に処理
        methods = ", ".join(getattr(route, "methods", []))
        path = getattr(route, "path", getattr(route, "url", "UNKNOWN"))
        print(f"{methods:8s} — {path}")

if __name__ == "__main__":
    main()