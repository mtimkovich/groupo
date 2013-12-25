import web
import jinja2 
import facebook

import yaml
import logging
import os
import sys


abspath = os.path.dirname(__file__)
sys.path.append(abspath)

import models

urls = (
        "/", "index",
)

template_dir = os.path.join(abspath, "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
        autoescape = True)

FACEBOOK_CONFIG_FILE = os.path.join(os.path.dirname(abspath), "facebook_api.yaml")

fb = open(FACEBOOK_CONFIG_FILE)
FACEBOOK = yaml.load(fb)
fb.close()

def render(template, **params):
    web.header("Content-Type", "text/html")
    t = jinja_env.get_template(template)
    return t.render(params)

class index:
    def GET(self):
        cookie = facebook.get_user_from_cookie(web.cookies(), FACEBOOK["id"], FACEBOOK["secret"])

        first_name = ""

        if cookie:
            graph = facebook.GraphAPI(cookie["access_token"])
            profile = graph.get_object("me")

            first_name = profile["first_name"]
            last_name = profile["last_name"]
            facebook_id = profile["id"]

            user = models.User.by_id(facebook_id)

            if not user:
                models.User.register(facebook_id, first_name, last_name)

        return render("index.html", first_name=first_name)

app = web.application(urls, globals())
application = app.wsgifunc()

