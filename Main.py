import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
import os
from UserDB import UserDB
from TaskBoardDB import TaskBoardDB
from TaskDB import TaskDB
from TaskBoardData import TaskBoardData
from EditTask import EditTask
from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],autoescape=True
)

class Main(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        userLoggedIn = users.get_current_user()
        user_TaskBoards = []
        TaskBoard_Count = 0
        Total_Tasks = []
        Active_Tasks = []
        Complete_Tasks = []
        Completed_Today = []

        if userLoggedIn:
            loginLink = users.create_logout_url(self.request.uri)
            loginStatus = 'Logout'
            user_Key = ndb.Key('UserDB', userLoggedIn.user_id()).get()
            if user_Key == None:
                user_Key = UserDB(id=userLoggedIn.user_id())
                user_Key.user_Email = userLoggedIn.email()
                user_Key.put()
            TaskBoardKeys = user_Key.TB_Key
            for i in TaskBoardKeys:
                user_TaskBoards.append(ndb.Key('TaskBoardDB',i).get())
            TaskBoard_Count = len(TaskBoardKeys)
            for j in range(0,TaskBoard_Count):
                Task_DB_Data = ndb.Key('TaskDB',TaskBoardKeys[j]).get()
                if Task_DB_Data != None:
                    Total_Tasks.append(len(Task_DB_Data.TaskTitle))
                    ActiveCount = 0
                    CompleteToday = 0
                    for k in range(0,len(Task_DB_Data.TaskCompleteStatus)):
                        if Task_DB_Data.TaskCompleteStatus[k] == 0:
                            ActiveCount = ActiveCount + 1
                        DateTimeToday = datetime.now()
                        DateToday = DateTimeToday.strftime('%Y-%m-%d')
                        if Task_DB_Data.TaskCompleteDate[k] == DateToday:
                            CompleteToday = CompleteToday + 1
                    Active_Tasks.append(ActiveCount)
                    Completed_Today.append(CompleteToday)
                    Complete_Tasks.append(len(Task_DB_Data.TaskTitle) - ActiveCount)
                else:
                    Total_Tasks.append(0)

        else:
            loginLink = users.create_login_url(self.request.uri)
            loginStatus = 'Login'

        template_values = {
            'loginLink' : loginLink,
            'loginStatus' : loginStatus,
            'userLoggedIn' : userLoggedIn,
            'user_TaskBoards' : user_TaskBoards,
            'TaskBoard_Count' : TaskBoard_Count,
            'Total_Tasks' : Total_Tasks,
            'Active_Tasks' : Active_Tasks,
            'Complete_Tasks' : Complete_Tasks,
            'Completed_Today' : Completed_Today
        }
        template = JINJA_ENVIRONMENT.get_template('Main.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        userLoggedIn = users.get_current_user()

        user_Fetch = ndb.Key('UserDB',userLoggedIn.user_id())
        user_DB_Data = user_Fetch.get()
        user_DB_TB = user_DB_Data.TB_Key

        New_TBName = self.request.get('NewTaskBoardName')
        TB_Key_String = userLoggedIn.email() + "" + New_TBName
        Match_Found = 0

        # In below code I am searching if my TB_Key is already present in my UserDB for loggedin user email or not.
        for i in user_DB_TB:
            if i == TB_Key_String:
                Match_Found = 1
                break
            else:
                Match_Found = 0

        # If entered TB name is not present in loggedin user, then Found must be 0.
        if Match_Found == 0:
            user_DB_Data.TB_Key.append(TB_Key_String)
            user_DB_Data.put()
            TBDB_Reference = ndb.Key('TaskBoardDB',TB_Key_String)
            TBDB_Reference = TBDB_Reference.get()
            TBDB_Reference = TaskBoardDB(id=TB_Key_String)
            TBDB_Reference.TBName = New_TBName
            TBDB_Reference.Admin_Email = userLoggedIn.email()
            TBDB_Reference.Users_Email.append(userLoggedIn.email())
            TBDB_Reference.put()
            self.redirect('/')
        else:
            self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', Main),
    ('/TaskBoardData', TaskBoardData),
    ('/EditTask', EditTask),
], debug=True)
