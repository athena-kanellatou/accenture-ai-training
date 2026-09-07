import datetime
import time

from fastapi import FastAPI

app = FastAPI()


@app.get("/sync")
def show_serial():
    time.sleep(5)

    return {
        "message": (
            "Σειριακή uvicorn απόκριση: "
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    }