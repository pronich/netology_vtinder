import sqlalchemy
from sqlalchemy import text

class DbTinder:
    def __init__(self, creds):
        self.creds = creds
        db = f'postgresql://{self.creds[0]}:{self.creds[1]}@localhost:5432/{self.creds[2]}'
        engine = sqlalchemy.create_engine(db)
        self.conn = engine.connect()
        if creds[3] == True:
            self._create_tables()

    def _create_tables(self):
        create_users = text('''create table if not exists users (
                        id serial primary key,
                        user_name varchar(100) not null,
                        sex integer not null,
                        city_id integer not null,
                        bdate integer not null);''')
        create_users_suggest = text('''create table if not exists users_suggest (
                        id serial primary key,
                        suggest_name varchar(100) unique not null,
                        link text not null,
                        user_id integer references users(id) not null
                        );''')
        create_user_photo = text('''create table if not exists user_photo (
                        id serial primary key,
                        suggest_id integer references users_suggest(id),
                        photo_link text not null
                        );''')
        cur = self.conn.execute(create_users)
        cur = self.conn.execute(create_users_suggest)
        cur = self.conn.execute(create_user_photo)
        return


    def check_user(self, user_name):
        check = text('''
                select id
                from users
                where user_name = :user_name;''')
        cur = self.conn.execute(check, user_name=user_name).fetchall()
        if cur == []:
            return None
        else:
            item_id = cur[0][0]
        return item_id

    def check_suggest(self, suggest_name):
        check = text('''
                        select id
                        from users_suggest
                        where suggest_name = :suggest_name;''')
        cur = self.conn.execute(check, suggest_name=suggest_name).fetchall()
        if cur == []:
            return None
        else:
            item_id = cur[0][0]
        return item_id

    def insert_user(self, user_info):

        insert = text('''
                    insert into users (user_name, sex, city_id, bdate) values (:user_name, :sex, :city_id, :bdate);''')
        cur = self.conn.execute(insert, user_name=user_info[0], sex=user_info[1], city_id=user_info[2], bdate=user_info[3])
        return self.check_user(user_info[0])

    def insert_suggest(self, item, user_id):
        insert = text('''
            insert into users_suggest (suggest_name, link, user_id) values (:suggest_name, :link, :user_id);''')
        cur = self.conn.execute(insert, suggest_name=item[0], link=item[1], user_id=user_id)
        return self.check_suggest(item[0])

    def insert_data(self, data):
        insert = text('''
                    insert into user_photo (suggest_id, photo_link) values (:suggest_id, :photo);''')
        suggest_id = data[0]
        for photo_link in data[1]:
            cur = self.conn.execute(insert, suggest_id=suggest_id, photo=photo_link)
        return 'Complete'

    def get_user_info(self, user_name):
        req = text('''
                select 
                    id,
                    user_name,
                    sex,
                    city_id,
                    bdate
                from users
                where user_name = :user_name;''')
        cur = self.conn.execute(req, user_name=user_name).fetchall()[0]
        return cur

    def get_users_data(self, user_id):
        req = text('''
        select 
            id,
            suggest_name,
            link
        from users_suggest
        where user_id = :user_id;''')
        cur = self.conn.execute(req, user_id=user_id).fetchall()
        return cur

    def get_users_photo(self, suggest_id):
        req = text('''
                select 
                    photo_link
                from user_photo
                where suggest_id = :suggest_id;''')
        cur = self.conn.execute(req, suggest_id=suggest_id).fetchall()
        return cur