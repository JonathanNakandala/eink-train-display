"""
Use Playwright to render page
"""
import os
import io
import asyncio

from playwright.async_api import async_playwright
from PIL import Image
from structlog import get_logger


log = get_logger()

DEFAULT_URL = "http://localhost:8000/index.html"


async def check_class_loaded(page):
    """
    There's a CSS class called `loaded` that indicates page is loaded
    """
    await page.wait_for_selector(".container")

    timeout = 30

    try:
        await asyncio.wait_for(check_loaded_class(page), timeout)
    except asyncio.TimeoutError as exc:
        raise asyncio.TimeoutError(
            f"Waiting for page load timed out after {timeout} seconds"
        ) from exc


async def check_loaded_class(page):
    """
    Evaluate Javascript to check if class is loaded
    """
    while not await page.evaluate(
        """() => {
        let container = document.querySelector(".container");
        return container ? container.classList.contains("loaded") : false;
    }"""
    ):
        await asyncio.sleep(0.05)


async def generate_image(page):
    """
    Once the page has loaded, generate screenshot
    The screenshot it stored in a file and returned as a Pillow Image
    """
    await page.screenshot(path="playwright-screenshot.png")
    screenshot_data = await page.screenshot(type="png")
    pil_image = Image.open(io.BytesIO(screenshot_data))
    pil_image = pil_image.convert("L")  # greyscale
    threshold = 128  # If it's a 0 or a 1 in the B/W image
    pil_image = pil_image.point(lambda p: p > threshold and 255)
    log.info(f"Image Dimensions: {pil_image.size}")
    return pil_image


async def render_webpage(url=DEFAULT_URL) -> Image:
    """
    Create a browser instance that renders the page
    """

    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch(args=["--disable-web-security"])
        context = await browser.new_context(
            viewport={"width": 800, "height": 480}, timezone_id="Europe/London"
        )
        page = await context.new_page()

        page.on("console", lambda msg: log.info(msg.text))

        page_url = os.getenv("PAGE_URL", url)
        log.info("Loading Webpage", url=page_url)
        await page.goto(page_url)

        await check_class_loaded(page)
        image = await generate_image(page)

        await browser.close()
        return image
