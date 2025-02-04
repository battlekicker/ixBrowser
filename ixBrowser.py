import io
import random
import time

from ixbrowser_local_api import IXBrowserClient
from loguru import logger
from playwright.async_api import async_playwright, expect


PROFILE_ID = 1


async def start(address: str):
    with async_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://{debugging_address}")
            # page = browser.contexts[0].pages[0] if browser.contexts else browser.contexts[0].new_page()

            logger.info("Заходим на сайт...")
            await page.goto("https://stackoverflow.com/")

            logger.success("Страница загружена!")

            await asyncio.sleep(999)

            accept_cookie_btn = mm_page.get_by_test_id('recovery-phrase-reveal')
            await expect(accept_cookie_btn).to_be_attached()
            await accept_cookie_btn.click()

            await asyncio.sleep(10)

        except Exception as e:
            logger.exception(f"Ошибка Playwright: {e}")
        finally:
            browser.close()


c = IXBrowserClient()
data = c.get_profile_list()
if data is None:
    print('Get profile list error:')
    print('Error code=', c.code)
    print('Error message=', c.message)
else:
    open_result = c.open_profile(PROFILE_ID, cookies_backup=False, load_profile_info_page=False)
    if open_result:
        debugging_address = open_result["debugging_address"]
        asyncio.run(start(debugging_address))
        c.close_profile(PROFILE_ID)
    else:
        logger.critical("Ошибка открытия профиля")

