import asyncio

from ixbrowser_local_api import IXBrowserClient
from loguru import logger
from playwright.async_api import async_playwright, expect


PROFILE_ID = 1


async def start():
    async with async_playwright() as p:
        try:
            context = await p.chromium.launch_persistent_context(
                '',
                headless=False,
                # slow_mo=600
            )

            page = await context.new_page()

            logger.info("Заходим на сайт...")
            await page.goto("https://stackoverflow.com/")
            await page.wait_for_load_state()

            logger.success("Страница загружена!")

            accept_cookie_btn = page.locator("//button[@id='onetrust-accept-btn-handler']")
            await expect(accept_cookie_btn).to_be_attached()
            await accept_cookie_btn.click()



            #await asyncio.sleep(999)
            await page.close()
            await context.close()
        except Exception as e:
            logger.exception(f"Ошибка Playwright: {e}")


c = IXBrowserClient()
data = c.get_profile_list()
# c.clear_profile_cache_and_cookies(PROFILE_ID)
if data is None:
    logger.error('Get profile list error. \n'
                 f'Error code={c.code}'
                 f'Error message={c.message}')
else:
    open_result = c.open_profile(PROFILE_ID, cookies_backup=False, load_profile_info_page=False)
    if open_result:

        asyncio.run(start())
        cookie = c.get_profile_cookie(PROFILE_ID)
        print(cookie)
        c.close_profile(PROFILE_ID)
    else:
        logger.critical("Ошибка открытия профиля")

