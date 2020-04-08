import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
import os
from UserDB import User_DB

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],autoescape=True
)

class Main(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        userLoggedIn = users.get_current_user()
        if userLoggedIn:
            loginLink = users.create_logout_url(self.request.uri)
            loginStatus = 'Logout'
            user_Key_Fetch = ndb.Key('User_DB', userLoggedIn.user_id())
            user_Key = user_Key_Fetch.get()
            if user_Key == None:
                user_Key = User_DB(id=userLoggedIn.user_id())
                user_Key.user_Email = userLoggedIn.email()
                user_Key.put()
        else:
            loginLink = users.create_login_url(self.request.uri)
            loginStatus = 'Login'

        template_values = {
            'loginLink' : loginLink,
            'loginStatus' : loginStatus,
            'userLoggedIn' : userLoggedIn
        }
        template = JINJA_ENVIRONMENT.get_template('Main.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', Main),
], debug=True)
