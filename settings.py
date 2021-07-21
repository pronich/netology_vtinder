# Tokens
group_token = ''
vk_login = ''
vk_password = ''

# Vk_group information
group_id = ''

# Database information
db_login = ''
db_password = ''
db_name = ''
create_db = False

# Dictionary with all information
settings = {
    'DB': {
        'login': db_login,
        'password': db_password,
        'db_name': db_name,
        'create_bd': create_db
    },
    'tokens': {
        'group_token': group_token,
        'login': vk_login,
        'password': vk_password
    },
    'vtinder_bot': {
        'group_id': group_id,
        'phrases':{
            'Welcome': 'Приветствую! Я бот, который ищет в твоем городе подходящую пару. Я подбираю ее по количеству лайков на фотографий и основных данных по тебе.\n'
                       'У меня есть несколько функций:\n'
                       '- "Find" - запрос на поиск новых вариантов,\n'
                       '- "Show" - я показываю то, что уже искал для тебя,\n',
           'Find friend': 'Напиши число, сколько вариантов для тебя найти?',
           'Fail': 'Дико извиняюсь, но я не понял твоей команды... Давай напомню о том, что я могу.\n'
                   'У меня есть несколько функций:\n'
                   '- "Find" - запрос на поиск новых вариантов,\n'
                   '- "Show" - я показываю то, что уже искал для тебя,\n',
           'Show results': 'Окей, смотри, что я для тебя уже находил',
           'Out of range': 'Я нашел все возможные варианты. Если хочешь их посмотреть, введи команду "Show results".'
        }
    }
}


