import web
import jinja2 
import psycopg2
import psycopg2.extras
import facebook

import yaml
import logging
import os

urls = (
        "/", "index",
)

template_dir = os.path.join(os.path.dirname(__file__), "static")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
        autoescape = True)

FACEBOOK_CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "facebook_api.yaml")
DB_CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.yaml")

fb = open(FACEBOOK_CONFIG_FILE)
db = open(DB_CONFIG_FILE)

FACEBOOK = yaml.load(fb)
DB_CONFIG = yaml.load(db)

fb.close()
db.close()

def db_str(dict):
    return " ".join(["{}={}".format(k, v) for (k, v) in dict.items()])

def render(template, **params):
    web.header("Content-Type", "text/html")
    t = jinja_env.get_template(template)
    return t.render(params)

class index:
    def GET(self):
        cookie = facebook.get_user_from_cookie(web.cookies(), FACEBOOK["id"], FACEBOOK["secret"])
        if cookie:
            graph = facebook.GraphAPI(cookie["access_token"])
            profile = graph.get_object("me")

            first_name = profile["first_name"]
            last_name = profile["last_name"]
            facebook_id = profile["id"]

            conn = psycopg2.connect(db_str(DB_CONFIG))
#             cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur = conn.cursor()
            cur.execute("select count (*) from users where facebook_id = %s;", (facebook_id,))
            count = cur.fetchone()

            if not count[0]:
                cur.execute("insert into users (facebook_id, first_name, last_name, created) values (%s, %s, %s, now());", (facebook_id, first_name, last_name))
                logging.info(cur.query)

            cur.execute("select * from users where facebook_id = %s;", (facebook_id,))
            count = cur.fetchone()
            conn.commit()

            cur.close()
            conn.close()

            return render("index.html", first_name=first_name, last_name=last_name, facebook_id=facebook_id, count=count)

        else:
            return render("index.html")

application = web.application(urls, globals()).wsgifunc()

