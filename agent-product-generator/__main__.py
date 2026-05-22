import signal
import subprocess
import sys
import threading


def _stream(proc: subprocess.Popen, prefix: str) -> None:
    for line in iter(proc.stdout.readline, b""):
        print(f"[{prefix}] {line.decode(errors='replace').rstrip()}", flush=True)


def main() -> None:
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    frontend = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port=8501"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    threading.Thread(target=_stream, args=(backend, "backend"), daemon=True).start()
    threading.Thread(target=_stream, args=(frontend, "frontend"), daemon=True).start()

    print("Backend  -> http://localhost:8000")
    print("Frontend -> http://localhost:8501")

    def shutdown(signum, frame):
        backend.terminate()
        frontend.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    backend.wait()
    frontend.terminate()


main()
