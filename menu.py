import asyncio

from ixbrowser_local_api import IXBrowserClient
from loguru import logger

from ixBrowser import start, save_cookie, print_cookie, update_profile_cookie

print('___________________________\n'
      '1. Нагулять куки\n'
      '2. Сохранить cookie в файл\n'
      '3. Вывести содержимое файла с cookie\n'
      '4. Заменить cookie профиля содержимым файла\n'
      '5. Завершить работу\n'
      '___________________________\n')


c = IXBrowserClient()
data = c.get_profile_list()
if data is None:
    logger.error('Get profile list error. \n'
                 f'Error code: {c.code}'
                 f'Error message: {c.message}')
else:
    while True:
        choice = int(input('Выберите номер пункта: '))
        print('___________________________\n')

        if choice == 1:
            asyncio.run(start(client=c, profile_id=1))
        elif choice == 2:
            print('___________________________\n'
                  '1. Перезаписать файл с cookie\n'
                  '2. Добавить cookie в файл\n'
                  '___________________________\n')
            choice = int(input('Выберите номер пункта: '))
            print('___________________________\n')

            if choice == 1:
                asyncio.run(save_cookie(client=c, profile_id=1, file="data.txt", rewrite=True))
            elif choice == 2:
                asyncio.run(save_cookie(client=c, profile_id=1, file="data.txt", rewrite=False))

        elif choice == 3:
            asyncio.run(print_cookie(file="data.txt"))
        elif choice == 4:
            asyncio.run(update_profile_cookie(client=c, profile_id=2, file="data.txt"))
        elif choice == 5:
            print('Завершение работы программы')
            break
