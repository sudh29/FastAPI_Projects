import subprocess
import os
import sys
import time


def main():
    # Get absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "backend")
    frontend_dir = os.path.join(base_dir, "frontend")

    print(f"🚀 Starting Project 9 from {base_dir}")

    processes = []

    try:
        # Start Backend
        print("\n[Backend] Starting FastAPI server...")
        # We use sys.executable -m uvicorn to ensure we use the current python environment
        backend_cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ]
        backend_proc = subprocess.Popen(
            backend_cmd, cwd=backend_dir, env=os.environ.copy()
        )
        processes.append(backend_proc)
        print("✅ Backend started on http://localhost:8000")

        # Start Frontend
        print("\n[Frontend] Starting Vite development server...")
        # npm needs shell=True on many systems to be found correctly, or we can assume it's in PATH
        # On Windows/WSL, shell=True is often safest for npm
        frontend_cmd = "npm run dev"
        frontend_proc = subprocess.Popen(
            frontend_cmd, cwd=frontend_dir, shell=True, env=os.environ.copy()
        )
        processes.append(frontend_proc)
        print(
            "✅ Frontend started (check output for URL, usually http://localhost:5173)"
        )

        print("\n⚡ Both services are running. Press Ctrl+C to stop all services.\n")

        # Wait for both processes
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("❌ Backend process exited unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("❌ Frontend process exited unexpectedly.")
                break

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping services...")
    finally:
        # Terminate all processes
        for p in processes:
            if p.poll() is None:
                try:
                    # Try graceful termination first
                    p.terminate()
                    # Give it a moment
                    try:
                        p.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        p.kill()
                except Exception as e:
                    print(f"Error stopping process: {e}")


if __name__ == "__main__":
    main()
