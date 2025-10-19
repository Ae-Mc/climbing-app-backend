import os
import pathlib
import signal
import sys
import time

sys.path.append(pathlib.Path(__file__).parent.parent.resolve().absolute().as_posix())

from uvicorn import run


def stop():
    time.sleep(1)
    os.kill(os.getpid(), signal.SIGTERM)


if __name__ == "__main__":
    USE_COLORS = True  # platform != "win32"
    signal.signal(
        signal.SIGINT,
        stop,  # type: ignore
    )
    if len(sys.argv) > 1 and sys.argv[1] == "--dev":
        if len(sys.argv) > 2:
            env_file = sys.argv[2]
        else:
            env_file = ".env"
        run(
            "climbing.main:app",
            host="0.0.0.0",
            port=80,
            use_colors=USE_COLORS,
            reload=True,
            env_file=env_file,
        )
    else:
        run(
            "climbing.main:app",
            host="0.0.0.0",
            port=80,
            use_colors=USE_COLORS,
        )
