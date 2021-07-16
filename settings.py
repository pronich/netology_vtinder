# Tokens
group_token = '62d3cd33a2553d14e036d5fe430ca43cca5e8131c4ee48729c3be4f4a215f5b64fc7e68220ba1da6076a7'
vk_login = 'xex103@yandex.ru'
vk_password = 'Xexpron456852'

# Vk_group information
group_id = '205637354'

# Database information
db_login = 'npronichev'
db_password = 'pronich13'
db_name = 'vtinder'
create_db = True

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
        'phrases': {
            'Welcome': 'Приветствую! Я бот, который ищет в твоем городе подходящую пару. '
                       'Я подбираю ее по количеству лайков на фотографий и основных данных по тебе.\n'
                       'У меня есть несколько функций:\n'
                       '- "Find" - запрос на поиск новых вариантов,\n'
                       '- "Show" - я показываю то, что уже искал для тебя,\n',
            'Find friend': 'Напиши число, сколько вариантов для тебя найти?',
            'Fail': 'Дико извиняюсь, но я не понял твоей команды... Давай напомню о том, что я могу.\n'
                    'У меня есть несколько функций:\n'
                    '- "Find friend" - запрос на поиск новых вариантов,\n'
                    '- "Show results" - я показываю то, что уже искал для тебя,\n',
            'Show results': 'Окей, смотри, что я для тебя уже находил',
            'Out of range': 'Я нашел все возможные варианты. Если хочешь их посмотреть, введи команду "Show results".'
        }
    }
}
