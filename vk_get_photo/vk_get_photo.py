from pprint import pprint
import vk_api


class VkApi:
    def __init__(self, vk_token):
        self.vk_session = vk_api.VkApi(token=vk_token)
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
            'user_ids': user_id
        }
        resp = self.vk_session.method('users.get', user_info)
        return resp

    def search(self, headers):
        resp = self.vk_session.method('users.search', headers)
        return resp

if __name__ == '__main__':
    vk_token = '3b6a64cc2a7bc5d48c28cee4f5102bdd743207cae6dfc4eb9de26f7e676ec8bbfcbc9c6cb8444eb26431a'
    vk = VkApi(vk_token)

    user_id = '79952187'
    # res = vk.get_all_photo(user_id)
    user_info = vk.get_info(user_id)[0]
    pprint(user_info)
    # pprint(res)
    headers = {
        'city': user_info['city']['id'],
        'sex': 2,
        'status': 6,
        'birth_year': 1995
    }
    pprint(vk.search(headers))