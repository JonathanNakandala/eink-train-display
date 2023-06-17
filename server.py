"""
Server to receive and display an image


"""
import structlog
import uvicorn
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from waveshare_epd import epd7in5_V2

log = structlog.get_logger()

app = FastAPI()


async def parse_body(request: Request):
    """
    Get the bytes for the body
    """
    data: bytes = await request.body()
    return data


def display_on_epd(data: bytes):
    """
    Send the bytes to the display
    """
    epd = epd7in5_V2.EPD()
    log.info("Initializing the display...")
    epd.init()
    epd.display(data)
    log.info("Sending display to sleep")
    epd.sleep()


@app.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    data: bytes = Depends(parse_body),
):
    """
    Send Data
    """
    byte_data = data

    file_size = len(byte_data)
    log.info(f"Received file size: {file_size} bytes", type=type(data), data=data)

    # Add the display operation as a background task
    background_tasks.add_task(display_on_epd, data)

    return {
        "message": "Data received and processing started",
        "file_size": file_size,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
