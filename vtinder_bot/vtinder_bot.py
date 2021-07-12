from vk_get_photo.vk_get_photo import VkApi
from vtinder_db.db_class import DbTinder
from settings import settings
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import random
from datetime import datetime
from pprint import pprint

login = settings['DB']['login']
password = settings['DB']['password']
db_name = settings['DB']['db_name']
create_bd = settings['DB']['create_bd']
group_token = settings['tokens']['group_token']
phrases = settings['vtinder_bot']['phrases']
vk_token = settings['tokens']['vk_token']

class Vtinder:
    def __init__(self):
        self.bot_session = vk_api.VkApi(token=group_token)
        self.db = DbTinder([login, password, db_name, create_bd])
        self.vk_get_photo = VkApi(vk_token)
        self.longpoll = VkLongPoll(self.bot_session)
        self.vk = self.bot_session.get_api()
        self.check_status = 0

    def listen_longpol(self):
        hashmap = {}
        for event in self.longpoll.listen():

            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if event.text.lower() in ['start', 'привет', 'hello', 'старт']:
                    self.vk.messages.send(  # Отправляем сообщение
                        user_id=event.user_id,
                        message=phrases['Welcome'],
                        random_id=random.randint(1000000, 9999999)
                    )
                elif event.text.lower() == 'find':
                    hashmap[event.user_id] = {'status': True,
                                              'date': datetime.now()}
                    self.vk.messages.send(  # Отправляем сообщение
                        user_id=event.user_id,
                        message=phrases['Find friend'],
                        random_id=random.randint(1000000, 9999999)
                    )
                elif self.check_status == 1:
                    try:
                        bdate = int(event.text)
                        self.check_status = 0
                        return bdate
                    except Exception:
                        self.vk.messages.send(  # Отправляем сообщение
                            user_id=event.user_id,
                            message='Мне нужен год рождения, без него я не смогу подобрать варианты. Напиши год числом',
                            random_id=random.randint(1000000, 9999999)
                        )
                elif event.text.lower() == 'show':
                    user_name = str(event.user_id)
                    collect_data = self.get_data_from_db(user_name)
                    for key, value in collect_data.items():
                        self.vk.messages.send(  # Отправляем сообщение
                            user_id=event.user_id,
                            message=f"{key}\n{value}\n\n",
                            random_id=random.randint(1000000, 9999999)
                        )
                elif event.user_id in hashmap and hashmap[event.user_id]['status'] == True:
                    if (datetime.now()-hashmap[event.user_id]['date']).seconds/60 > 1:
                        self.vk.messages.send(  # Отправляем сообщение
                            user_id=event.user_id,
                            message=phrases['Fail'],
                            random_id=random.randint(1000000, 9999999)
                        )
                    else:
                        try:
                            count = int(event.text)
                            user_id = str(event.user_id)
                            collect_data = self.collect_data(user_id, count)
                            if collect_data == None:
                                self.vk.messages.send(  # А может его в файл генерить?
                                    user_id=event.user_id,
                                    message=phrases['Out of range'],
                                    random_id=random.randint(1000000, 9999999)
                                )
                            else:
                                for key, value in collect_data.items():
                                    self.vk.messages.send(  # А может его в файл генерить?
                                        user_id=event.user_id,
                                        message=f"{key}\n{value}\n\n",
                                        random_id=random.randint(1000000, 9999999)
                                    )
                        except Exception:
                            self.vk.messages.send(  # Отправляем сообщение
                                user_id=event.user_id,
                                message='Для поиска мне нужно число. Давай попробуем еще раз',
                                random_id=random.randint(1000000, 9999999)
                            )
                else:
                    self.vk.messages.send(  # Отправляем сообщение
                        user_id=event.user_id,
                        message=phrases['Fail'],
                        random_id=random.randint(1000000, 9999999)
                    )

    def get_users(self, user_id, count):
        user_info = self.vk_get_photo.get_info(user_id)[0]
        bdate = user_info['bdate']
        try:
            bdate = bdate.split('.')[2]
        except IndexError:
            self.check_status = 1
            self.vk.messages.send(  # А может его в файл генерить?
                user_id=user_id,
                message='Чтобы выполнить правильный поиск, напиши год своего рождения',
                random_id=random.randint(1000000, 9999999)
            )
            bdate = self.listen_longpol()
            print(type(bdate))
        if user_info['sex'] == 2:
            sex = 1
        else:
            sex = 2
        headers = {
            'city': user_info['city']['id'],
            'sex': sex,
            'status': 6,
            'birth_year': bdate
        }
        users = self.vk_get_photo.search(headers)['items']
        users_lst = []
        for idx, user in enumerate(users):
            if self.db.check_suggest(str(user['id'])) is None and user['is_closed'] == False:
                users_lst.append(user)
                if len(users_lst) == count:
                    return [users_lst, count]
        if users_lst == []:
            return None
        return [users_lst, len(users_lst)]

    def get_best_photos(self, user_id):
        resp = self.vk_get_photo.get_max_size_photos(user_id)
        if resp is None:
            return None
        else:
            photo_dic = resp[1]
            values = list(photo_dic.values())
            values.sort()
            photo = {}
            for key, value in photo_dic.items():
                if value in values[-3:]:
                    photo[key] = value
            return photo

    def get_best_users(self, user_id, count):
        users_id = self.db.check_user(user_id)
        if users_id == None:
            users_id = self.db.insert_user(user_id)
        users = self.get_users(user_id, count)
        if users == None:
            return {'items': []}
        elif users[1] < count:
            self.vk.messages.send(  # Отправляем сообщение
                user_id=user_id,
                message=f'Я смог найти только {users[1]} вариантов',
                random_id=random.randint(1000000, 9999999)
            )
        json = {'items': []}
        for user in users[0]:
            suggest_name = str(user['id'])
            photo_dic = self.get_best_photos(suggest_name)
            if photo_dic is None:
                continue
            else:
                link = f'vk.com/id{suggest_name}'
                self.db.insert_suggest([str(suggest_name), link], users_id)
                suggest_id = self.db.check_suggest(str(suggest_name))
                self.db.insert_data([suggest_id, list(photo_dic.keys())])
                json['items'].append({'user_id': suggest_name, 'photos': photo_dic, 'link': link})
        pprint(json)
        return json

    def collect_data(self, user_id, count=5):
        json = self.get_best_users(user_id, count)
        if json['items'] == []:
            return None
        collect_data = {}
        for item in json['items']:
            collect_data[item['user_id']] = '\n'.join([item['link'], '\n'.join(list(item['photos'].keys()))])
        return collect_data


    def get_data_from_db(self, user_name):
        user_id = self.db.check_user(user_name)
        data = self.db.get_users_data(user_id)
        collect_data = {}
        json = {'items': []}
        for user in data:
            photos = self.db.get_users_photo(user[0])
            photo_link = []
            for photo in photos:
                photo_link.append(photo[0])
            collect_data[user[1]] = '\n'.join([user[2], '\n'.join(photo_link)])
            json['items'].append({'user_id': user[1], 'photos': photo_link, 'link': user[2]})
        pprint(json)
        return collect_data
