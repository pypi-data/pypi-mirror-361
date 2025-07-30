"""
Run Stinger API service directly with: python -m stinger.api
"""

import os
import sys

try:
    import uvicorn

    from stinger.api.app import app
except ImportError:
    print("Error: API dependencies not installed.")
    print("Please install with: pip install stinger-guardrails-alpha[api]")
    sys.exit(1)


def main():
    """Run the API server."""
    # Get configuration from environment or defaults
    host = os.getenv("STINGER_API_HOST", "127.0.0.1")
    port = int(os.getenv("STINGER_API_PORT", "8888"))
    reload = os.getenv("STINGER_API_RELOAD", "false").lower() == "true"

    # Check for command line arguments
    if "--reload" in sys.argv:
        reload = True
    if "--host" in sys.argv:
        idx = sys.argv.index("--host")
        if idx + 1 < len(sys.argv):
            host = sys.argv[idx + 1]
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])

    # Detached/background mode
    if "--detached" in sys.argv or "--background" in sys.argv:
        # Use platform-appropriate paths
        if sys.platform == "win32":
            import tempfile

            temp_dir = tempfile.gettempdir()
            log_file = os.path.join(temp_dir, "stinger-api.log")
            pid_file = os.path.join(temp_dir, "stinger-api.pid")
        else:
            log_file = "/tmp/stinger-api.log"
            pid_file = "/tmp/stinger-api.pid"

        # Platform-specific detached mode
        if sys.platform == "win32":
            # Windows: Use subprocess with CREATE_NEW_CONSOLE flag
            import subprocess

            # Create startup info to hide console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            # Start new process
            cmd = [sys.executable, "-m", "stinger.api", "--host", host, "--port", str(port)]

            with open(log_file, "a") as log:
                process = subprocess.Popen(
                    cmd,
                    stdout=log,
                    stderr=log,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS,
                )

            print(f"🚀 Starting Stinger API server at http://{host}:{port}")
            print(f"📚 Documentation available at http://{host}:{port}/docs")
            print(f"📋 Process ID: {process.pid}")
            print(f"📄 Logs: {log_file}")
            print(f"✋ To stop: taskkill /PID {process.pid} /F")

            # Write PID file
            with open(pid_file, "w") as f:
                f.write(str(process.pid))

            sys.exit(0)
        else:
            # Unix/Linux/macOS: Use fork
            pid = os.fork()
            if pid > 0:
                # Parent process
                print(f"🚀 Starting Stinger API server at http://{host}:{port}")
                print(f"📚 Documentation available at http://{host}:{port}/docs")
                print(f"📋 Process ID: {pid}")
                print(f"📄 Logs: {log_file}")
                print("✋ To stop: kill $(cat /tmp/stinger-api.pid)")

                # Write PID file
                with open(pid_file, "w") as f:
                    f.write(str(pid))

                sys.exit(0)

            # Child process - detach from terminal
            os.setsid()
            os.umask(0)

            # Redirect output to log file
            with open(log_file, "a") as log:
                sys.stdout = log
                sys.stderr = log

                # Print startup message to log
                print(f"🚀 Starting Stinger API server at http://{host}:{port}")
                print(f"📚 Documentation available at http://{host}:{port}/docs")
                print("Press CTRL+C to stop\n")

                # Run the server
                uvicorn.run(
                    app,
                    host=host,
                    port=port,
                    reload=False,  # No reload in detached mode
                    log_level="info",
                )
    else:
        # Normal mode
        print(f"🚀 Starting Stinger API server at http://{host}:{port}")
        print(f"📚 Documentation available at http://{host}:{port}/docs")
        print("Press CTRL+C to stop\n")

        uvicorn.run(
            "stinger.api.app:app" if reload else app,
            host=host,
            port=port,
            reload=reload,
            log_level="info",
        )


if __name__ == "__main__":
    main()
