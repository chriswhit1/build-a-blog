#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                    autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        response_content = self.render_str(template, **kw)
        self.write(response_content)

class MainPage(Handler):
    def render_front(self, title="", blogpost="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog "
                            "ORDER BY created DESC "
                            "LIMIT 5 ")
        self.render("front.html", title=title, blogpost=blogpost, error=error, blogs=blogs)

    def get(self):
        self.render_front()

class Blog(db.Model):
    title = db.StringProperty(required = True)
    blogpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class NewPage(Handler):
    def get(self):
        self.render_newpage()

    def render_newpage(self, title="", blogpost="", error=""):
        self.render("newpost.html", title=title, blogpost=blogpost, error=error)

    def post(self):
        title = self.request.get("title")
        blogpost = self.request.get("blogpost")

        if title and blogpost:
            a = Blog(title = title, blogpost = blogpost)
            a.put()
            id = a.key().id()
            self.redirect("/blog/%s" % id)
        else:
            error = "We need a blog!"
            self.render_newpage(title, blogpost, error)


class ViewPostHandler(MainPage):
    def get(self, post_id):
        post_int = int(post_id)
        post = Blog.get_by_id(post_int)

        if post:
            self.render("post.html", title=post.title, blogpost=post.blogpost)





#self.key().id()????

app = webapp2.WSGIApplication([
    ('/blog/', MainPage),
    ('/newpost', NewPage),
    webapp2.Route('/blog/<post_id:\d+>', ViewPostHandler)
], debug=True)
