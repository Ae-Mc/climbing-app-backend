from uvicorn import run

from climbing.main import app

if __name__ == "__main__":
    try:
        run("climbing.main:app", host="0.0.0.0", port=8000, reload=True)
    except ImportError:
        run(app, host="0.0.0.0", port=8000)
