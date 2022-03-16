from sys import platform

from uvicorn import run

from climbing.main import app

if __name__ == "__main__":
    USE_COLORS = platform != "win32"
    try:
        run(
            "climbing.main:app",
            host="0.0.0.0",
            port=80,
            reload=True,
            use_colors=USE_COLORS,
        )
    except ImportError:
        run(
            app,  # type: ignore
            host="0.0.0.0",
            port=80,
            use_colors=USE_COLORS,
        )
