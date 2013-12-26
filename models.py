import psycopg2
import psycopg2.extras
import yaml
import os

abspath = os.path.dirname(__file__)
DB_CONFIG_FILE = os.path.join(os.path.dirname(abspath), "database.yaml")

db = open(DB_CONFIG_FILE)

def db_str(dict):
    return " ".join(["{}={}".format(k, v) for (k, v) in dict.items()])

DB_CONFIG = db_str(yaml.load(db))

db.close()

class User:
    def __init__(self, row):
        self.id = row["id"]
        self.facebook_id = row["facebook_id"]
        self.first_name = row["first_name"]
        self.last_name = row["last_name"]
        self.created = row["created"]

    # Find user by facebook id
    @classmethod
    def by_id(cls, id):
        conn = psycopg2.connect(DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("select * from users where facebook_id = %s;", (id,))
        row = cur.fetchone()

        if row is None:
            u = None
        else:
            u = User(row)

        cur.close()
        conn.close()

        return u

    # Add user to users database
    @classmethod
    def register(cls, facebook_id, first_name, last_name):
        conn = psycopg2.connect(DB_CONFIG)
        cur = conn.cursor()

        cur.execute("insert into users (facebook_id, first_name, last_name, created) values (%s, %s, %s, now());", (facebook_id, first_name, last_name))
        logging.info(cur.query)
        conn.commit()

        cur.close()
        conn.close()
