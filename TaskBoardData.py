import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
import os
from UserDB import UserDB
from TaskBoardDB import TaskBoardDB
from TaskDB import TaskDB

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],autoescape=True
)

class TaskBoardData(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        userLoggedIn = users.get_current_user()
        TaskBoard_ID = self.request.get('id')

        if userLoggedIn:
            loginLink = users.create_logout_url(self.request.uri)
            loginStatus = 'Logout'
            user_Key_Fetch = ndb.Key('UserDB', userLoggedIn.user_id())
            user_Key = user_Key_Fetch.get()
            if user_Key == None:
                user_Key = UserDB(id=userLoggedIn.user_id())
                user_Key.user_Email = userLoggedIn.email()
                user_Key.put()
            TBData = ndb.Key('TaskBoardDB',TaskBoard_ID)
            TBData = TBData.get()
            AllUser_Email = UserDB.query()
        else:
            loginLink = users.create_login_url(self.request.uri)
            loginStatus = 'Login'
            TBData = ''
            AllUser_Email = ''
            self.redirect('/')

        template_values = {
            'loginLink' : loginLink,
            'loginStatus' : loginStatus,
            'userLoggedIn' : userLoggedIn,
            'TBData' : TBData,
            'AllUser_Email' : AllUser_Email
        }
        template = JINJA_ENVIRONMENT.get_template('TaskBoardData.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        userLoggedIn = users.get_current_user()
        TaskBoard_ID = self.request.get('id')

        if self.request.get('SubmitButton') == 'Invite From DB':
            UserEmailFromSelectBox = self.request.get('Select_Email_From_DB')
            self.InviteUser(UserEmailFromSelectBox,TaskBoard_ID)
        elif self.request.get('SubmitButton') == 'Invite By Email':
            UserEmailFromTextBox = self.request.get('UserEmailFromTB')
            self.InviteUser(UserEmailFromTextBox,TaskBoard_ID)
        else:
            self.redirect('/')

    def InviteUser(self, FetchUserEmail, TaskBoard_ID):
        user_Fetch = UserDB.query(UserDB.user_Email == FetchUserEmail)
        user_DB_Data = user_Fetch.get()
        user_DB_TB = user_DB_Data.TB_Key
        Match_Found = 0
        for i in user_DB_TB:
            if i == TaskBoard_ID:
                Match_Found = 1
                break
            else:
                Match_Found = 0
        if Match_Found == 0:
            user_DB_Data.TB_Key.append(TaskBoard_ID)
            user_DB_Data.put()
            TB_DB_Data = ndb.Key('TaskBoardDB',TaskBoard_ID)
            TB_DB_Data = TB_DB_Data.get()
            TB_DB_Data.Users_Email.append(FetchUserEmail)
            TB_DB_Data.put()
            self.redirect('/TaskBoardData?id='+TaskBoard_ID)
        else:
            self.redirect('/TaskBoardData?id='+TaskBoard_ID)

app = webapp2.WSGIApplication([
    ('/TaskBoardData',TaskBoardData),
], debug=True)
