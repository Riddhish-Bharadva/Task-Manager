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

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class Main(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        # Declaration of required variables starts here.
        user_TaskBoards = []
        TaskBoard_Count = 0
        Total_Tasks = []
        Active_Tasks = []
        Complete_Tasks = []
        Completed_Today = []
        # Declaration of required variables ends here.

        userLoggedIn = users.get_current_user() # Fetching data of loggedin user.

        if userLoggedIn: # Checking if user is logged in. IF logged in, this variable will not be None.
            loginLink = users.create_logout_url(self.request.uri)
            loginStatus = 'Logout'
            user_Key = ndb.Key('UserDB', userLoggedIn.email()).get() # Fetching data from UserDB table for logged in user.
            if user_Key == None: # In case no data is fetched from UserDB table, insert below values to same.
                user_Key = UserDB(id=userLoggedIn.email()) # User id will be same as email id.
                user_Key.user_Email = userLoggedIn.email() # Email id will be given by user while loging in.
                user_Key.put()
            TaskBoardKeys = user_Key.TB_Key # Fetching all taskboard Keys for given user. It contains keys of taskboards
            if TaskBoardKeys != None:
                for i in TaskBoardKeys: # Fetching all taskboard data from Taskboard DataStore.
                    user_TaskBoards.append(ndb.Key('TaskBoardDB',i).get())
                TaskBoard_Count = len(TaskBoardKeys) # Getting count of number of taskboard keys this user have.
                for j in range(0,TaskBoard_Count): # Looping to fetch data of tasks from TaskDB for all task boards fetched in above loop.
                    Task_DB_Data = ndb.Key('TaskDB',TaskBoardKeys[j]).get()
                    if Task_DB_Data != None:
                        Total_Tasks.append(len(Task_DB_Data.TaskTitle)) # Fetching total number of tasks in taskboard.
                        ActiveCount = 0 # Initializing for each task.
                        CompleteToday = 0 # Initializing for each task.
                        for k in range(0,len(Task_DB_Data.TaskCompleteStatus)): # Fetching total number of tasks completed in taskboard.
                            if Task_DB_Data.TaskCompleteStatus[k] == 0: # If TaskCompleteStatus is 0, task in incomplete.
                                ActiveCount = ActiveCount + 1 # If task is incomplete, active task count will be increamented.
                            DateTimeToday = datetime.now() # Fetching today's date and time.
                            DateToday = DateTimeToday.strftime('%Y-%m-%d') # Separating date from datetime.
                            if Task_DB_Data.TaskCompleteDate[k] == DateToday: # If task is completed, check if its completed today.
                                CompleteToday = CompleteToday + 1 # If true for above condition, increment Completed Today count by 1.
                        Active_Tasks.append(ActiveCount) # Appending in global variable.
                        Completed_Today.append(CompleteToday) # Appending in global variable.
                        Complete_Tasks.append(len(Task_DB_Data.TaskTitle) - ActiveCount) # Calculating completed task and appending in global variable.
                    else:
                        # In case there are no tasks in taskboard, append 0 to all.
                        Total_Tasks.append(0)
                        Active_Tasks.append(0)
                        Complete_Tasks.append(0)
                        Completed_Today.append(0)
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

        user_DB_Data = ndb.Key('UserDB',userLoggedIn.email()).get()

        ButtonValue = self.request.get('submitButton')

        if ButtonValue == 'Create':
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
        elif ButtonValue == "Proceed":
            if user_DB_Data.TB_Key == []: # Check if there are no Task board left for this user id, proceed to delete.
                user_DB_Data.key.delete()
                loginStatus = 'Login'
                self.redirect(users.create_logout_url(self.request.uri))
            else: # If there are task boards present, nothing will happen and user will be redirected to home page back.
                self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', Main),
    ('/TaskBoardData', TaskBoardData),
    ('/EditTask', EditTask),
], debug=True)
