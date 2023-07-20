"""
Use Playwright to render page
"""
import io
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
from PIL import Image
from structlog import get_logger
from .utils import send_to_server

log = get_logger()

PORT = 8927


def start_http_server(port, directory):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    httpd = HTTPServer(("localhost", port), Handler)
    httpd.serve_forever()


def render_webpage() -> Image:
    """
    Create a browser instance that renders the page
    """
    webpage_path = (
        Path(__file__).resolve().parent / ".." / "render" / "svelte" / "build"
    ).resolve()
    server_thread = Thread(target=start_http_server, args=(PORT, webpage_path))
    server_thread.daemon = True
    server_thread.start()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(args=["--disable-web-security"])
        context = browser.new_context(viewport={"width": 800, "height": 480})
        page = context.new_page()

        log.info("Loading Webpage")
        page.on("console", lambda msg: log.info(msg.text))
        page.goto(f"http://localhost:{PORT}/index.html")

        def check_class_loaded():
            return page.evaluate(
                """() => {
                return document.querySelector(".container").classList.contains("loaded");
            }"""
            )

        while not check_class_loaded():
            pass

        page.screenshot(path="playwright-screenshot.png")
        screenshot_data = page.screenshot(type="png")
        pil_image = Image.open(io.BytesIO(screenshot_data))
        pil_image = pil_image.convert("L")
        # Convert the image to binary black and white using a threshold value
        threshold = 128  # Adjust the threshold value as needed
        pil_image = pil_image.point(lambda p: p > threshold and 255)
        log.info(f"Image Dimensions: {pil_image.size}")
        browser.close()
        send_to_server(pil_image)
        return pil_image
