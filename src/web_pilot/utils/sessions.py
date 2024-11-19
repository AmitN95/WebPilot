import pydantic as pyd
import pyppeteer
import asyncio

from web_pilot.exc import InvalidSessionIDError
from web_pilot.utils.snapshot_util import SnapshotUtil
from web_pilot.schemas.pages import Snapshot, PageContent


# Utils
@pyd.validate_arguments
def break_session_id_to_parts(session_id: str) -> tuple:
    try:
        pool_id, browser_id, page_id = session_id.split("_")
        return (pool_id, browser_id, page_id)

    except ValueError:
        raise InvalidSessionIDError("Invalid session ID")


# Page actions
async def perform_action_click(page: pyppeteer.page.Page, **kwargs) -> None:
    if selector := kwargs.pop("selector", None) is None:
        raise ValueError(f"Selector is required for 'click' action")

    wait_for_selector = kwargs.pop("waitForSelector", True)
    options = kwargs.pop("options", None)
    if wait_for_selector:
        await page.waitForSelector(selector)
    await page.click(selector, options)


async def perform_action_authenticate(page: pyppeteer.page.Page, **kwargs) -> None:
    credentials = kwargs.pop("credentials")
    await page.authenticate(credentials)


async def perform_action_setUserAgent(page: pyppeteer.page.Page, **kwargs) -> None:
    user_agent = kwargs.pop("user_agent")
    await page.setUserAgent(user_agent)


async def perform_action_screenshot(page: pyppeteer.page.Page, **kwargs) -> None:
    options = kwargs.pop("options", None)
    await page.screenshot(options)


async def perform_action_goto(page: pyppeteer.page.Page, **kwargs) -> None:
    async def _wait_for_text(
        page: pyppeteer.page.Page, text: str, timeout: int = 30000, interval: int = 500
    ) -> bool:
        elapsed = 0
        while elapsed < timeout:
            content = await page.content()
            if text in content:
                return True
            await asyncio.sleep(interval / 1000)
            elapsed += interval
        raise asyncio.TimeoutError(f"Timeout: Could not find '{text}' in the page content.")

    url = kwargs.pop("url", None)
    if not url:
        raise ValueError("URL is required for 'goto' action")

    options = kwargs.pop("options", None)
    await page.goto(url, options)
    if kwargs.get("waitForText"):
        await _wait_for_text(page, kwargs.get("waitForText"))


async def perform_action_goBack(page: pyppeteer.page.Page, **kwargs) -> None:
    options = kwargs.pop("options", None)
    await page.goBack(options)


async def perform_action_goForward(page: pyppeteer.page.Page, **kwargs) -> None:
    options = kwargs.pop("options", None)
    await page.goForward(options)


async def perform_action_saveSnapshot(page: pyppeteer.page.Page) -> Snapshot:
    return await SnapshotUtil.capture_session_snapshot(page)


async def perform_action_restoreSnapshot(page: pyppeteer.page.Page, snapshot: Snapshot) -> None:
    await SnapshotUtil.restore_session(page, snapshot)


async def perform_action_setViewport(page: pyppeteer.page.Page, **kwargs) -> None:
    width = kwargs.pop("width")
    height = kwargs.pop("height")
    await page.setViewport({"width": width, "height": height})


async def perform_action_setCookie(page: pyppeteer.page.Page, **kwargs) -> None:
    cookies = kwargs.pop("cookies")
    await page.setCookie(*cookies)


async def perform_action_deleteCookie(page: pyppeteer.page.Page, **kwargs) -> None:
    cookies = kwargs.pop("cookies", None)
    all_ = kwargs.pop("all", False)
    if all_:
        await page.deleteCookies()
    else:
        await page.deleteCookie(*cookies)


async def perform_action_evaluate(page: pyppeteer.page.Page, **kwargs) -> None:
    code = kwargs.pop("code")
    args = kwargs.pop("args", [])
    return await page.evaluate(code, *args)


async def perform_action_evaluateOnNewDocument(page: pyppeteer.page.Page, **kwargs) -> None:
    code = kwargs.pop("code")
    args = kwargs.pop("args", [])
    return await page.evaluateOnNewDocument(code, *args)


async def perform_action_evaluateHandle(page: pyppeteer.page.Page, **kwargs) -> None:
    code = kwargs.pop("code")
    args = kwargs.pop("args", [])
    return await page.evaluateHandle(code, *args)


async def perform_action_addScriptTag(page: pyppeteer.page.Page, **kwargs) -> None:
    url = kwargs.pop("url")
    return await page.addScriptTag(url=url)


async def perform_action_removeScriptTag(page: pyppeteer.page.Page, **kwargs) -> None:
    handle = kwargs.pop("handle")
    return await page.removeScriptTag(handle)


async def perform_action_exposeFunction(page: pyppeteer.page.Page, **kwargs) -> None:
    name = kwargs.pop("name")
    code = kwargs.pop("code")
    return await page.exposeFunction(name, code)


async def perform_action_removeFunction(page: pyppeteer.page.Page, **kwargs) -> None:
    name = kwargs.pop("name")
    return await page.removeFunction(name)


async def perform_action_extractPageContents(page: pyppeteer.page.Page) -> PageContent:
    return PageContent(
        url=page.url,
        title=await page.title(),
        content=await page.content(),
    ).dict()


async def perform_action_setGeoLocation(page: pyppeteer.page.Page, **kwargs) -> None:
    latitude = kwargs.pop("latitude")
    longitude = kwargs.pop("longitude")
    await page.setGeolocation({"latitude": latitude, "longitude": longitude})


async def perform_action_clearGeolocation(page: pyppeteer.page.Page) -> None:
    await page.setGeolocation(None)


async def perform_action_emulateMedia(page: pyppeteer.page.Page, **kwargs) -> None:
    media_type = kwargs.pop("mediaType")  # Literal["screen", "print", "none"]
    await page.emulateMedia(media_type)


async def perform_action_setContent(page: pyppeteer.page.Page, **kwargs) -> None:
    content = kwargs.pop("content")
    await page.setContent(content)


async def perform_action_start_js_coverage(page: pyppeteer.page.Page) -> None:
    await page.coverage.startJSCoverage()


async def perform_action_stop_js_coverage(page: pyppeteer.page.Page) -> list[dict]:
    return await page.coverage.stopJSCoverage()


async def perform_action_get_accessibility_tree(page: pyppeteer.page.Page) -> dict:
    return await page.accessibility.snapshot()
