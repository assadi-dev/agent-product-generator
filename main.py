import os
import signal
import subprocess
import sys
import threading


def _stream(proc: subprocess.Popen, prefix: str) -> None:
    for line in iter(proc.stdout.readline, b""):
        print(f"[{prefix}] {line.decode(errors='replace').rstrip()}", flush=True)


def main() -> None:
    streamlit_port = os.environ.get("PORT", "8501")
    api_port = os.environ.get("API_PORT", "8000")

    backend = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn", "backend.main:app",
            "--host", "0.0.0.0",
            "--port", api_port,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    frontend = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "frontend/app.py",
            f"--server.port={streamlit_port}",
            "--server.address=0.0.0.0",
            "--server.headless=true",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    threading.Thread(target=_stream, args=(backend, "backend"), daemon=True).start()
    threading.Thread(target=_stream, args=(frontend, "frontend"), daemon=True).start()

    print(f"Backend  -> http://0.0.0.0:{api_port}", flush=True)
    print(f"Frontend -> http://0.0.0.0:{streamlit_port}", flush=True)

    def shutdown(signum, frame):
        backend.terminate()
        frontend.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    backend.wait()
    frontend.terminate()


main()
