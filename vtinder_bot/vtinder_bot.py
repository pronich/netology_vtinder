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
vk_login = settings['tokens']['login']
vk_password = settings['tokens']['password']
# vk_token = settings['tokens']['vk_token']

class VkApi:
    def __init__(self, vk_login, vk_password):
        self.vk_session = vk_api.VkApi(vk_login, vk_password)
        self.vk_session.auth(token_only=True)
        self.owner_id = self.vk_session.method('users.get')[0]['id']

    def get_user_id(self, user_id=None):
        user_name = {'user_ids': user_id}
        resp = self.vk_session.method('users.get', user_name)
        return resp[0]['id']

    def get_all_photo(self, user_id):
        try:
            user_id = int(user_id)
        except Exception:
            user_id = self.get_user_id(user_id)
        # user_id = str(user_id)
        photos_params = {
            'album_id': 'profile',
            'owner_id': user_id,
            'photo_sizes': 1,
            'extended': 1
        }
        resp = self.vk_session.method('photos.get', photos_params)
        return resp

    def get_max_size_photos(self, user_id=None):
        if user_id is None:
            user_id = self.owner_id
        all_photos = self.get_all_photo(user_id)
        json_file = []
        photo_dic = {}
        print('\nПолучаем фотографии максимального размера из VK')
        try:
            for photo in all_photos['items']:
                photo_name = str(photo['likes']['count']) + '.jpg'
                photo_size = photo['sizes'][len(photo['sizes']) - 1]['type']
                json_file.append({'file_name': photo_name, 'size': photo_size})
                photo_dic[photo['sizes'][len(photo['sizes']) - 1]['url']] = photo_name
            return [json_file, photo_dic]
        except IndexError:
            return None

    def get_info(self, user_id=None):
        if user_id is None:
            user_id = self.owner_id
        else:
            try:
                user_id = int(user_id)
            except 'get_user_id':
                user_id = self.get_user_id(user_id)
        user_info = {
            'fields': 'sex,bdate,city,relation',
            # 'fields': 'sex',
            'user_ids': user_id
        }
        resp = self.vk_session.method('users.get', user_info)
        return resp

    def search(self, headers):
        resp = self.vk_session.method('users.search', headers)
        return resp

    def get_city_id(self, city):
        headers = {
            'country_id': '1',
            'q': city
        }
        resp = self.vk_session.method('database.getCities', headers)['items'][0]['id']
        return resp

class Vtinder:
    def __init__(self):
        self.bot_session = vk_api.VkApi(token=group_token)
        self.db = DbTinder([login, password, db_name, create_bd])
        self.vk_get_photo = VkApi(vk_login, vk_password)
        self.longpoll = VkLongPoll(self.bot_session)
        self.vk = self.bot_session.get_api()
        self.get_bdate = 0
        self.get_city = 0
        self.get_info = 0

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
                elif event.text.lower() in ['find', 'find friends']:
                    if self.db.check_user(str(event.user_id)) != None:
                        hashmap[event.user_id] = {'status': True,
                                                  'date': datetime.now()}
                        self.vk.messages.send(  # Отправляем сообщение
                            user_id=event.user_id,
                            message=phrases['Find friend'],
                            random_id=random.randint(1000000, 9999999)
                        )
                    else:
                        user_info = self.vk_get_photo.get_info(event.user_id)[0]
                        keys = list(user_info.keys())
                        if 'city' not in keys and 'bdate' not in keys:
                            self.get_info = 1
                            self.vk.messages.send(
                                user_id=event.user_id,
                                message='Чтобы выполнить правильный поиск, напиши город, в котором ты живешь',
                                random_id=random.randint(1000000, 9999999)
                            )
                            info = self.listen_longpol()
                            city = info[0]
                            city = self.vk_get_photo.get_city_id(city)
                            bdate = info[1]
                        elif 'city' not in keys:
                            self.get_city = 1
                            self.vk.messages.send(
                                user_id=event.user_id,
                                message='Чтобы выполнить правильный поиск, напиши город, в котором ты живешь',
                                random_id=random.randint(1000000, 9999999)
                            )
                            city = self.listen_longpol()
                            city = self.vk_get_photo.get_city_id(city)
                        elif 'bdate' not in keys:
                            self.get_bdate = 1
                            self.vk.messages.send(
                                user_id=event.user_id,
                                message='Чтобы выполнить правильный поиск, напиши год своего рождения',
                                random_id=random.randint(1000000, 9999999)
                            )
                            bdate = self.listen_longpol()
                        else:
                            bdate = user_info['bdate']
                            city = user_info['city']['id']
                            try:
                                bdate = bdate.split('.')[2]
                            except IndexError:
                                self.get_bdate = 1
                                self.vk.messages.send(  # А может его в файл генерить?
                                    user_id=event.user_id,
                                    message='Чтобы выполнить правильный поиск, напиши год своего рождения',
                                    random_id=random.randint(1000000, 9999999)
                                )
                                bdate = self.listen_longpol()
                                print(type(bdate))


                        user_info = [str(event.user_id), user_info['sex'], city, bdate]
                        self.db.insert_user(user_info)

                        hashmap[event.user_id] = {'status': True,
                                                  'date': datetime.now()}
                        self.vk.messages.send(  # Отправляем сообщение
                            user_id=event.user_id,
                            message=phrases['Find friend'],
                            random_id=random.randint(1000000, 9999999)
                        )
                elif self.get_bdate == 1:
                    try:
                        bdate = int(event.text)
                        self.get_bdate = 0
                        return bdate
                    except Exception:
                        self.vk.messages.send(  # Отправляем сообщение
                            user_id=event.user_id,
                            message='Мне нужен год рождения, без него я не смогу подобрать варианты. Напиши год числом',
                            random_id=random.randint(1000000, 9999999)
                        )
                elif self.get_city == 1:
                    city = event.text
                    self.get_city = 0
                    return city
                elif self.get_info == 1:
                    city = event.text
                    self.get_info = 0
                    self.get_bdate = 1
                    self.vk.messages.send(
                        user_id=event.user_id,
                        message='Чтобы выполнить правильный поиск, напиши год своего рождения',
                        random_id=random.randint(1000000, 9999999)
                    )
                    bdate = self.listen_longpol()
                    return [city, bdate]

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
                            self.vk.messages.send(
                                user_id=event.user_id,
                                message='Собирайю информацию, подождите...',
                                random_id=random.randint(1000000, 9999999)
                            )

                            collect_data = self.collect_data(user_id, count)
                            if collect_data == None:
                                self.vk.messages.send(
                                    user_id=event.user_id,
                                    message=phrases['Out of range'],
                                    random_id=random.randint(1000000, 9999999)
                                )
                            else:
                                for key, value in collect_data.items():
                                    self.vk.messages.send(
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
        client = self.db.get_user_info(user_id)
        if client[2] == 2:
            sex =1
        else:
            sex = 2
        headers = {
            'sex': sex,
            'city_id': client[3],
            'birth_year': client[4],
            'status': 6
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
                    if len(photo) == 3:
                        return photo
            return photo

    def get_best_users(self, user_id, count):
        users_id = self.db.check_user(user_id)
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
