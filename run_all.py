import subprocess
import sys
import time


def main():
    api_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--reload"])
    time.sleep(3)
    ui_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])

    try:
        api_process.wait()
        ui_process.wait()
    except KeyboardInterrupt:
        api_process.terminate()
        ui_process.terminate()


if __name__ == "__main__":
    main()
