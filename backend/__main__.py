import signal
import subprocess
import sys
import threading
import uvicorn


def _stream(proc: subprocess.Popen, prefix: str) -> None:
    for line in iter(proc.stdout.readline, b""):
        print(f"[{prefix}] {line.decode(errors='replace').rstrip()}", flush=True)


def main() -> None:
    frontend = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port=8501"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    threading.Thread(target=_stream, args=(frontend, "frontend"), daemon=True).start()

    def shutdown(signum, frame):
        frontend.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        uvicorn.run("backend.main:app", host="0.0.0.0", port=8000)
    finally:
        frontend.terminate()


if __name__ == "__main__":
    main()
