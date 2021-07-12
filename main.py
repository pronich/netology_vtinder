from vtinder_bot.vtinder_bot import Vtinder
from settings import settings

vk_token = settings['tokens']['vk_token']

if __name__ == '__main__':
    vtinder = Vtinder()
    vtinder.listen_longpol()
    # vtinder.get_users_from_db()
    # vtinder.collect_data('34376460')
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
