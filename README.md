# VTinder

## Описание
Перед вами бот, который поможет найти для себя вторую половинку:)
Программа собирает информацию по вам, и ищет подходящие варианты из вашего города по критериям:
* Статус в отношениях. Ищем людей, которые в поиске
* Возраст. Ищем людей схожего с вами возраста

Программа делает глобальный поиск по заданным параметрам и выбирает лучших из списка.
Сам процесс выглядит так:
1. Делаем глобальный поиск по людям
1. Заходим на страничку пользователя и собираем фотографии
1. Выбираем 3 фотографии с большим количеством фотографий
1. Выводим в сообщении варианты:
    1. Id пользователя или UserName
    1. Ссылка на профиль
    1. Фотографии
    
1. Сохраняем информацию в БД

```JSON
{'items':  [
  {
    'link': 'тут ссылка',
    'photos': {
      'link1': 'name = кол-ву лайков',
      'link2': 'name = кол-ву лайков'
    },
    'user_id': 'id user или user_name'
  }
]}
```
## Как попробовать бота
Перейдите по ссылке и начните общение, нажав на "Написать сообщение". 
Ссылка: https://vk.com/public205637354.
Откроется чат, в котором можно начать работать с ботом.
У бота есть несколько основных команд:
* Start, которую также можно инициализировать как "Привет", "Hello", "Старт". После этого будет приветствие от бота.
* Find. Команда, по которой запускается поиск вариантов. Данная функция имеет дополнительный запрос на количество вариантов. Также, если у вас скрыт год рождения, то бот сделает дополнительный запрос.
* Show. Показывает варианты, которые были найдены раньше.

## Как запустить бота самому (Подготовка файла Settings.py)
### Создание БД
Чтобы программа отрабатывала корректно и сохраняла данные в БД, необходимо поднять PosgreSQL базу данных.
1. Через админа создаем новую базу данных. Название необходимо запомнить и внести в settings.py в поле 'db_name'
   ```python
   create database <name>;
1. Через админа создаем пользователя, который будет управлять данным приложением. Логин и пароль от пользователя вносим в файл settings.py в поля 'db_login' & 'db_password'
   ```python
   create user <name> with password '<pass>';
1. Назначаем нового пользователя владельцем нашей БД
   ```python
   alter database <db_name> owner to <user_name>;
1. В Settings.py укажите create_db = True (По умолчанию стоит False). В этом случае таблицы будут сгенерированы автоматически.   
1. Если вы сами готовы создать таблицы, то в settings.py необходимо указать create_db = False. Код для создания таблиц:
    ```python
   create table if not exists users (
        id serial primary key,
        user_name varchar(100) not null);
   
   create table if not exists users_suggest (
        id serial primary key,
        suggest_name varchar(100) unique not null,
        link text not null,
        user_id integer references users(id) not null
        );
   
   create table if not exists user_photo (
        id serial primary key,
        suggest_id integer references users_suggest(id),
        photo_link text not null
        );

### Получение токенов
В данном приложении используется 2 токена:
* Токен пользователя для поиска вариантов и фотографий
* Токен сообщества, для чатбота

#### VK_token
Необходимо получить VKToken по документация VK: https://vk.com/dev/implicit_flow_user.
При получение токена доступа необходимо указать, что нужен доступ к друзьям и фото.
Токен необходимо прописать в Settings.py в поле 'vk_token'.
Для упрощения, ниже запрос. Исправьте параметры client_id
```python
https://oauth.vk.com/authorize?client_id=1&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends,groups&response_type=token&v=5.131
```

#### Group_token
Для получения Group_token необходимо:
1. Создать публичную страницу VK
2. Зайти в настройки публичной страницы.
    1. Выберите работа с API и выберите longpoll api
    2. Сообщения -> настройки для бота -> включите "Добавить кнопку начать"
    3. Получите токен доступа по инструкции https://vk.com/dev/access_token?f=2.%20Ключ%20доступа%20сообщества\n
    
    Ниже пример запроса для получения токена. Скопируйте его в настройки API сообщества
   
```python
https://oauth.vk.com/authorize?client_id=1&group_ids=1&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=messages&response_type=token&v=5.131
```

### Запуск программы
Для запуска программы необходимо запустить файл main.py
В этот момент запустится LongPoll session. Эта сессия позволяет слышать сообщения из вконтакте от пользователей.
При получении сообщений запускается логика бота, которая ищет подходящие варианты и отправляет сообщение тому, кто это запросил.

## Исключения
Бот работает только в личных сообщениях. Добавлять его в беседы на текущий момент нельзя.