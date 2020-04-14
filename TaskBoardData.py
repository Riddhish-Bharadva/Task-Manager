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
            TB_DB_Data = ndb.Key('TaskBoardDB',TaskBoard_ID).get()
            FetchUserEmail = self.request.get('SelectToInviteUser')
            user_DB_Data = UserDB.query(UserDB.user_Email == FetchUserEmail).get()
            if userLoggedIn.email() == TB_DB_Data.Admin_Email:
                Match_Found = 0
                for i in user_DB_Data.TB_Key:
                    if i == TaskBoard_ID:
                        Match_Found = 1
                        break
                    else:
                        Match_Found = 0
                if Match_Found == 0:
                    user_DB_Data.TB_Key.append(TaskBoard_ID)
                    user_DB_Data.put()
                    TB_DB_Data.Users_Email.append(FetchUserEmail)
                    TB_DB_Data.put()
                    self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=UserInvited')
                else:
                    self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=UserAlreadyExist')
            else:
                self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=UserNotAdminOfThisTask')

# Below if condition is to remove user from taskboard.
        elif self.request.get('SubmitButton') == 'Remove':
            TB_DB_Data = ndb.Key('TaskBoardDB',TaskBoard_ID).get()
            Task_DB_Data = ndb.Key('TaskDB',TaskBoard_ID).get()
            FetchUserEmail = self.request.get('SelectToRemoveUser')
            user_DB_Data = UserDB.query(UserDB.user_Email == FetchUserEmail).get()
            if userLoggedIn.email() == TB_DB_Data.Admin_Email:
                UDB_Match_Found = 0
                TB_DB_Match_Found = 0
                position_UDB = -1
                position_TB_DB = -1
                for i in range(0,len(user_DB_Data.TB_Key)):
                    if user_DB_Data.TB_Key[i] == TaskBoard_ID:
                        UDB_Match_Found = 1
                        position_UDB = i
                        break
                for j in range(0,len(TB_DB_Data.Users_Email)):
                    if TB_DB_Data.Users_Email[j] == FetchUserEmail:
                        TB_DB_Match_Found = 1
                        position_TB_DB = j
                        break
                if Task_DB_Data != None:
                    for k in range(0,len(Task_DB_Data.TaskAssignedUser)):
                        if Task_DB_Data.TaskAssignedUser[k] == FetchUserEmail:
                            Task_DB_Data.TaskAssignedUser[k] = "Not Assigned"
                            Task_DB_Data.put()
                            TB_DB_Data.TaskConnect.TaskAssignedUser[k] = "Not Assigned"
                            TB_DB_Data.put()
                if UDB_Match_Found == 1:
                    del user_DB_Data.TB_Key[position_UDB]
                    user_DB_Data.put()
                    if TB_DB_Match_Found == 1:
                        del TB_DB_Data.Users_Email[position_TB_DB]
                        TB_DB_Data.put()
                        self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=UserRemoved')
                else:
                    self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=UserNotExistInTaskBoard')
            else:
                self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=UserNotAdminOfThisTask')

# Below elif condition is to handle creating a new task.
        elif self.request.get('SubmitButton') == 'Create Task':
            NewTaskTitle = self.request.get('NewTaskTitle')
            TaskDueDate = self.request.get('TaskDueDate')
            TaskDueDate = datetime.strptime(TaskDueDate,'%Y-%m-%d')
            Task_DB_Data = ndb.Key('TaskDB', TaskBoard_ID).get()
            Match_Found = 0
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

# Below code is to handle Assign Task Modal.
        elif self.request.get('SubmitButton') == 'Assign':
            TaskTitle = self.request.get('TaskTitleTextBox')
            SelectionOfUser = self.request.get('SelectToAssignUser')
            TB_DB_Data = ndb.Key('TaskBoardDB', TaskBoard_ID).get()
            Task_DB_Data = ndb.Key('TaskDB', TaskBoard_ID).get()
            ListNumber = 0
            for i in range(0, len(Task_DB_Data.TaskTitle)):
                if Task_DB_Data.TaskTitle[i] == TaskTitle:
                    ListNumber = i
                    break
            if Task_DB_Data.TaskAssignedUser[i] == 'Not Assigned':
                Task_DB_Data.TaskAssignedUser[i] = SelectionOfUser
                Task_DB_Data.put()
                TB_DB_Data.TaskConnect = Task_DB_Data
                TB_DB_Data.put()
                self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=UserAssignedToTaskSuccessfully')
            else:
                self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=UserAlreadyAssignedForThisTask')

# If no condition matches, user will be redirected to home page.
        elif self.request.get('SubmitButton') == 'Delete':
            User_DB_Data = ndb.Key('UserDB', userLoggedIn.user_id()).get()
            TB_DB_Data = ndb.Key('TaskBoardDB', TaskBoard_ID).get()
            if TB_DB_Data.TaskConnect == None:
                if len(TB_DB_Data.Users_Email) == 1:
                    if TB_DB_Data.Users_Email[0] == userLoggedIn.email():
                        for i in range(0, len(User_DB_Data.TB_Key)):
                            if User_DB_Data.TB_Key[i] == TaskBoard_ID:
                                del TB_DB_Data.TBName
                                del TB_DB_Data.Admin_Email
                                del TB_DB_Data.Users_Email
                                del TB_DB_Data.TaskConnect
                                TB_DB_Data.put()
                                del User_DB_Data.TB_Key[i]
                                User_DB_Data.put()
                                self.redirect('/')
                            else:
                                self.response.write('There was some error while deleting task board.')
                    else:
                        self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=UserNotAdmin')
                else:
                    self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=UsersStillAssigned')
            else:
                self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=TaskStillExist')

# If no condition matches, user will be redirected to home page.
        else:
            self.redirect('/')

app = webapp2.WSGIApplication([
    ('/TaskBoardData',TaskBoardData),
], debug=True)
