"""
Server to receive and display an image


"""
import structlog

from fastapi import FastAPI, Request, Depends
import uvicorn

from waveshare_epd import epd7in5_V2

log = structlog.get_logger()

app = FastAPI()


async def parse_body(request: Request):
    """
    Get the bytes for the body
    """
    data: bytes = await request.body()
    return data


@app.post("/upload")
async def upload_file(data: bytes = Depends(parse_body)):
    """
    Send Data
    """
    byte_data = data

    file_size = len(byte_data)
    log.info(f"Received file size: {file_size} bytes", type=type(data), data=data)
    epd = epd7in5_V2.EPD()
    log.info("Initialising the display...")
    epd.init()
    epd.display(data)
    log.info("Sending Display to Sleep")
    epd.sleep()
    return {"message": "Bytearray received and processed successfully!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
