"""
Use Playwright to render page
"""
import io
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
from structlog import get_logger
from .utils import send_to_server

log = get_logger()


def render_webpage() -> Image:
    """
    Create a browser instance that renders the page
    """
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(args=["--disable-web-security"])
        context = browser.new_context(viewport={"width": 800, "height": 480})
        page = context.new_page()

        file_path = (
            Path(__file__).resolve().parent
            / ".."
            / "render"
            / "svelte"
            / "build"
            / "index.html"
        ).resolve()
        log.info(f"Loading Webpage: {file_path}")
        page.on("console", lambda msg: log.info(msg.text))
        page.goto(f"file://{file_path}")

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
