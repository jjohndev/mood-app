from flask import g
from constants import DATABASE
from sqlite3 import connect


class DBConn(object):
    def get_db(self):
        """
        returns a connection the the DB, unless we have one open, in which case returns the existing one
        """
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = connect(DATABASE)
        return db

    def query_db(self, query, args=(), one=False):
        """
        str query: the SQL query to hit the DB with
        tuple args: this allows us to use sqlite's query param injection, wo fear of sql injection
        bool one: pass if expecting a singular result
        used for select statements, as this does not contain a commit
        note that in order to use the kwarg args with only 1 parameter, you must pass the kwarg val as a tuple e.g. args=(single_val,)
        """
        try:
            cur = self.get_db().execute(query, args)
            rv = cur.fetchall()
            cur.close()
        except Exception as e:
            print(e)
            return False
        return (rv[0] if rv else None) if one else rv

    def edit_db(self, query, args=()):
        """
        similar to query_db but contains a commit for insert, update and delete queries
        """
        conn = self.get_db()
        try:
            cur = conn.execute(query, args)
            conn.commit()
            cur.close()
        except Exception as e:
            print(e)
            return False
        return True

    def close_connection(self, exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()
