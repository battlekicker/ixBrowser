import asyncio
import json
import os
import re

from loguru import logger
from playwright.async_api import async_playwright, expect

SITE_ADDRESS = "https://stackoverflow.com/"
PROFILE_ID = 1
PROFILE2_ID = 2
FILE = 'data.txt'


async def start(client, profile_id):
    open_result = client.open_profile(profile_id, cookies_backup=False, load_profile_info_page=False)
    if open_result:
        ws_endpoint = open_result['ws']
        if ws_endpoint:
            logger.info(f'Profile ID: {profile_id} | Opened. WS Endpoint: {ws_endpoint}')
            async with async_playwright() as p:
                try:
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
        else:
            logger.critical("Error getting WebSocket endpoint")
        logger.info(f'Profile ID: {profile_id} | Cookie: \n'
                    f'{client.get_profile_cookie(profile_id)}')
        client.close_profile(profile_id)
    else:
        logger.critical("Error opening profile")


async def save_cookie(client, profile_id, file, rewrite):
    cookies = client.get_profile_cookie(profile_id)
    cookies = json.loads(cookies)
    if rewrite:
        await rewrite_file(cookies, file)
    else:
        await add_to_file(cookies, file)
    logger.info(f'Profile ID: {profile_id} | Cookie saved in file "{file}".')


async def rewrite_file(cookies, file):
    logger.info(f'Rewriting file "{file}".')
    with open(file, 'w') as outfile:
        for cookie in cookies:
            cookie_str = json.dumps(cookie)
            outfile.writelines(cookie_str + ',\n')


async def add_to_file(cookies, file):
    logger.info(f'Adding to file "{file}".')
    if os.path.exists(file):
        with open(file, 'a') as outfile:
            for cookie in cookies:
                cookie_str = json.dumps(cookie)
                outfile.writelines(cookie_str + ',\n')
    else:
        with open(file, 'w') as outfile:
            for cookie in cookies:
                cookie_str = json.dumps(cookie)
                outfile.writelines(cookie_str + ',\n')


async def get_cookie(file):
    with open(file, 'r') as f:
        raw_data = f.read()
    # Оборачиваем JSON-объекты в список
    json_str = f"[{raw_data.strip()}]"
    # Убираем лишние `\n`
    json_str = json_str.replace("\n", "")
    # Удаляем лишнюю запятую перед `]` (если есть)
    json_str = re.sub(r",\s*]$", "]", json_str)

    return json_str


async def print_cookie(file):
    with open(file, 'r') as f:
        for line in f:
            print(line)


async def update_profile_cookie(client, profile_id, file):
    logger.info(f'Profile ID: {profile_id} | Cookie: \n'
                f'{client.get_profile_cookie(PROFILE2_ID)}')
    cookie = await get_cookie(file)
    if cookie != '':
        rs = client.update_profile_cookie(profile_id, cookie)
        print(rs)
        logger.info(f'Profile ID: {profile_id} | Cookie updated.')
        logger.info(f'Profile ID: {profile_id} | Cookie: \n'
                    f'{client.get_profile_cookie(profile_id)}')
    else:
        logger.error('Cookie file is empty!')
