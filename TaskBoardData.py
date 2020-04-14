import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
import os
from UserDB import UserDB
from TaskBoardDB import TaskBoardDB
from TaskDB import TaskDB
from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],autoescape=True
)

class TaskBoardData(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        userLoggedIn = users.get_current_user()
        TaskBoard_ID = self.request.get('id')
        TaskCount = 0
        notification = ''

        if userLoggedIn:
            loginLink = users.create_logout_url(self.request.uri)
            loginStatus = 'Logout'
            user_Key_Fetch = ndb.Key('UserDB', userLoggedIn.user_id())
            user_Key = user_Key_Fetch.get()
            if user_Key == None:
                user_Key = UserDB(id=userLoggedIn.user_id())
                user_Key.user_Email = userLoggedIn.email()
                user_Key.put()
            TBData = ndb.Key('TaskBoardDB',TaskBoard_ID).get()
            TaskData = ndb.Key('TaskDB', TaskBoard_ID).get()
            if TaskData != None:
                TaskCount = len(TaskData.TaskTitle)
            AllUser_Email = UserDB.query()
            notification = self.request.get('notification')
            if notification == '':
                notification = 'No Notification'
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
            'AllUser_Email' : AllUser_Email,
            'TaskCount' : TaskCount,
            'notification' : notification
        }
        template = JINJA_ENVIRONMENT.get_template('TaskBoardData.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'

        userLoggedIn = users.get_current_user()
        TaskBoard_ID = self.request.get('id')

# Below if condition is to invite user to taskboard.
        if self.request.get('SubmitButton') == 'Invite':
            FetchUserEmail = self.request.get('SelectToInviteUser')
            user_DB_Data = UserDB.query(UserDB.user_Email == FetchUserEmail).get()
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
                self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=UserInvited')
            else:
                self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=UserAlreadyExist')

# Below elif condition is to handle creating a new task.
        elif self.request.get('SubmitButton') == 'Create Task':
            NewTaskTitle = self.request.get('NewTaskTitle')
            TaskDueDate = self.request.get('TaskDueDate')
            TaskDueDate = datetime.strptime(TaskDueDate,'%Y-%m-%d')
            Task_DB_Data = ndb.Key('TaskDB', TaskBoard_ID).get()
            if Task_DB_Data != None:
                Task_Title_List = Task_DB_Data.TaskTitle
                for i in Task_Title_List:
                    if i == NewTaskTitle:
                        Match_Found = 1
                        break
                    else:
                        Match_Found = 0
            else:
                Match_Found = 0
            if Match_Found == 0:
                if Task_DB_Data == None:
                    Task_DB_Data = TaskDB(id=TaskBoard_ID)
                Task_DB_Data.TaskTitle.append(NewTaskTitle)
                Task_DB_Data.TaskDueDate.append(TaskDueDate)
                Task_DB_Data.TaskAssignedUser.append('Not Assigned')
                Task_DB_Data.TaskCompleteStatus.append(0)
                Task_DB_Data.TaskCompleteDate.append('NA')
                Task_DB_Data.TaskCompleteTime.append('NA')
                Task_DB_Data.put()
                TB_DB_Data = ndb.Key('TaskBoardDB',TaskBoard_ID).get()
                TB_DB_Data.TaskConnect = Task_DB_Data
                TB_DB_Data.put()
                self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=CreateTaskSuccessful')
            else:
                self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=CreateTaskFailed')

# Below code is to handle Completion Status Checkbox.
        elif self.request.get('SubmitButton') == 'Yes':
            TaskCompletionCheckBoxTitle = self.request.get('TastCompleteStatusTextBox')
            TB_DB_Data = ndb.Key('TaskBoardDB', TaskBoard_ID).get()
            Task_DB_Data = ndb.Key('TaskDB', TaskBoard_ID).get()
            ListNumber = 0
            for i in range(0, len(Task_DB_Data.TaskTitle)):
                if Task_DB_Data.TaskTitle[i] == TaskCompletionCheckBoxTitle:
                    ListNumber = i
                    break
            DateTimeToday = datetime.now()
            DateToday = DateTimeToday.strftime('%Y-%m-%d')
            TimeToday = DateTimeToday.strftime("%X")
            if Task_DB_Data.TaskCompleteStatus[i] == 0:
                Task_DB_Data.TaskCompleteStatus[i] = 1
                Task_DB_Data.TaskCompleteDate[i] = DateToday
                Task_DB_Data.TaskCompleteTime[i] = TimeToday
                Task_DB_Data.put()
                TB_DB_Data.TaskConnect = Task_DB_Data
                TB_DB_Data.put()
                self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=TaskCompleteStatusChangedToComplete')
            elif Task_DB_Data.TaskCompleteStatus[i] == 1:
                Task_DB_Data.TaskCompleteStatus[i] = 0
                Task_DB_Data.TaskCompleteDate[i] = 'NA'
                Task_DB_Data.TaskCompleteTime[i] = 'NA'
                Task_DB_Data.put()
                TB_DB_Data.TaskConnect = Task_DB_Data
                TB_DB_Data.put()
                self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=TaskCompleteStatusChangedToNotComplete')
            else:
                self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=TaskCompleteStatusNotChanged')

# In case no condition from above satisfies, below redirects user to home page.
        else:
            self.redirect('/')

app = webapp2.WSGIApplication([
    ('/TaskBoardData',TaskBoardData),
], debug=True)
