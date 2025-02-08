import asyncio
import json
import pprint
import os.path

from ixbrowser_local_api import IXBrowserClient
from loguru import logger
from playwright.async_api import async_playwright, expect


SITE_ADDRESS = "https://stackoverflow.com/"
PROFILE_ID = 1
PROFILE2_ID = 2
FILE = 'data.txt'


async def start(ws_endpoint: str):
    async with async_playwright() as p:
        try:
            # context = await p.chromium.launch_persistent_context(
            #     '',
            #     headless=False,
            #     # slow_mo=600
            # )

            browser = await p.chromium.connect_over_cdp(ws_endpoint)  # Подключаемся к ixBrowser через CDP
            context = browser.contexts[0]

            if context.pages:
                page = context.pages[0]
            else:
                page = await context.new_page()

            logger.info(f"{SITE_ADDRESS} | Entering the site.")
            await page.goto(SITE_ADDRESS)
            await page.wait_for_load_state()

            logger.success(f"{SITE_ADDRESS} | Page successfully loaded!")

            try:
                accept_cookie_btn = page.locator("//button[@id='onetrust-accept-btn-handler']")
                await expect(accept_cookie_btn).to_be_attached()
                await accept_cookie_btn.click()
            except:
                pass

            users_btn = page.locator("//a[@id='nav-users']")
            await expect(users_btn).to_be_attached()
            await users_btn.click()

            await asyncio.sleep(2)
            await page.close()
            await context.close()
        except Exception as e:
            logger.exception(f"Playwright error | {e}")


async def save_cookie(client, file):
    cookie = client.get_profile_cookie(PROFILE_ID)
    cookie = json.loads(cookie)
    if os.path.exists(file):
        with open(file, 'a') as outfile:
            outfile.write(',')
            cookie_str = json.dumps(cookie[0])
            outfile.write(cookie_str)
    else:
        with open(file, 'w') as outfile:
            cookie_str = json.dumps(cookie[0])
            outfile.write(cookie_str)

    logger.info(f'Cookie saved in file "{file}".')
    #pprint.pp(cookie[0])


async def get_cookie(file):
    with open(file, 'r') as f:
        cookie = f.readlines()
    return cookie


c = IXBrowserClient()
data = c.get_profile_list()
# c.clear_profile_cache_and_cookies(PROFILE_ID)
if data is None:
    logger.error('Get profile list error. \n'
                 f'Error code={c.code}'
                 f'Error message={c.message}')
else:

    # Работа с первым профилем
    open_result = c.open_profile(PROFILE_ID, cookies_backup=False, load_profile_info_page=False)
    print(open_result)
    if open_result:
        ws_endpoint = open_result['ws']
        if ws_endpoint:
            logger.info(f'Profile ID: {PROFILE_ID} | Opened. WS Endpoint: {ws_endpoint}')
            asyncio.run(start(ws_endpoint))
        else:
            logger.critical("Error getting WebSocket endpoint")
        logger.info(f'Profile ID: {PROFILE_ID} | Cookie: \n'
                    f'{c.get_profile_cookie(PROFILE_ID)}')
        asyncio.run(save_cookie(c, FILE))
        c.close_profile(PROFILE_ID)
    else:
        logger.critical("Error opening profile")
    logger.info(f'Profile ID: {PROFILE2_ID} | Cookie: \n'
                f'{c.get_profile_cookie(PROFILE2_ID)}')

    # Работа со вторым профилем
    cookie = asyncio.run(get_cookie(FILE))
    cookie = str(cookie).replace("['", "[").replace("']", "]").replace("\\n', '", " ")
    if cookie != '':
        c.update_profile_cookie(PROFILE2_ID, cookie)
        logger.info(f'Profile ID: {PROFILE2_ID} | Cookie updated.')
        logger.info(f'Profile ID: {PROFILE2_ID} | Cookie: \n'
                    f'{c.get_profile_cookie(PROFILE2_ID)}')
    else:
        logger.error('Cookie file is empty!')


