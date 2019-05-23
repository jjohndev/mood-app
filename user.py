from string import ascii_uppercase, digits
from random import choice
from datetime import datetime, timedelta
from dateutil.parser import parse
from dbconn import DBConn


class User(DBConn):
    def login_user(self, username, password):
        """
        queries the DB for a User ID based on creds
        if one is found, automatically generates a new unique key good for 1 hour
        """
        user_id = self.query_db('select UserID from users where username=? and password=?', args=(username, password), one=True)
        if user_id is not False:
            if user_id[0]:
                return self.update_user_key(user_id[0])
        return False

    def key_generator(self):
        """
        generates a random alphanumeric uppercase sequence of length 25 for use as a unique, security key
        """
        return ''.join(choice(ascii_uppercase + digits) for _ in range(25))

    def update_user_key(self, user_id, expiration=1):
        """
        inserts a new key into the DB for the user, sets expiration time to 1 hour by default
        """
        user_key = self.key_generator()
        if self.edit_db('update users set key=?, key_exp=? where UserID=?', args=(
            str(user_key),
            str((datetime.now() + timedelta(hours=expiration)).isoformat()),
            user_id
        )):
            return user_key
        return False

    def check_auth(self, key):
        """
        str key: key header from post request, authenticates user
        if key is in the DB associated with a user record and has not yet expired, returns user ID, otherwise returns False 
        """
        result = self.query_db('select UserID, key_exp from users where key=?', args=(key,), one=True)
        if result:
            user_id, key_exp = result
            if user_id:
                if datetime.now() < parse(key_exp):
                    return user_id
        return False
