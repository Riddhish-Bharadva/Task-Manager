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

class EditTask(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        userLoggedIn = users.get_current_user()
        TaskBoard_ID = self.request.get('id')
        Old_TaskTitle = self.request.get('tasktitle')
        RequiredTaskData = []

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
                for i in range(0, len(TaskData.TaskTitle)):
                    if TaskData.TaskTitle[i] == Old_TaskTitle:
                        RequiredTaskData.append(TaskData.TaskTitle[i])
                        RequiredTaskData.append(TaskData.TaskDueDate[i])
                        RequiredTaskData.append(TaskData.TaskAssignedUser[i])
        else:
            loginLink = users.create_login_url(self.request.uri)
            loginStatus = 'Login'
            TBData = ''
            self.redirect('/')

        template_values = {
            'loginLink' : loginLink,
            'loginStatus' : loginStatus,
            'userLoggedIn' : userLoggedIn,
            'TBData' : TBData,
            'TaskData' : RequiredTaskData,
            'Old_TaskTitle' : Old_TaskTitle
        }
        template = JINJA_ENVIRONMENT.get_template('EditTask.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'
        userLoggedIn = users.get_current_user()

        TaskBoard_ID = self.request.get('id')
        Old_TaskTitle = self.request.get('Old_TaskTitle')

        New_TaskTitle = self.request.get('TaskTitleTB')
        New_TaskDueDate = self.request.get('TaskDueDate')
        #New_TaskDueDate = datetime.strptime(New_TaskDueDate,'%Y-%m-%d')
        New_AssignUser = self.request.get('SelectToAssignUser')

        TB_DB_Data = ndb.Key('TaskBoardDB',TaskBoard_ID).get()
        Task_DB_Data = ndb.Key('TaskDB', TaskBoard_ID).get()
        Old_TaskTitle_Position = -1
        for i in range(0,len(Task_DB_Data.TaskTitle)):
            if Task_DB_Data.TaskTitle[i] == Old_TaskTitle:
                Old_TaskTitle_Position = i
                break

        if self.request.get('SubmitButton') == 'Edit':
            New_TaskTitle_Match_Found = 0
            for i in range(0,len(Task_DB_Data.TaskTitle)):
                if Task_DB_Data.TaskTitle[i] == New_TaskTitle:
                    New_TaskTitle_Match_Found = 1
                    break
            if New_TaskTitle_Match_Found == 0:
                if Old_TaskTitle_Position != -1:
                    Task_DB_Data.TaskTitle[Old_TaskTitle_Position] = New_TaskTitle
                    Task_DB_Data.TaskDueDate[Old_TaskTitle_Position] = New_TaskDueDate
                    Task_DB_Data.TaskAssignedUser[Old_TaskTitle_Position] = New_AssignUser
                    Task_DB_Data.put()
                    TB_DB_Data.TaskConnect = Task_DB_Data
                    TB_DB_Data.put()
                    self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=TaskDataEditedSuccessfully')
            else:
                if Old_TaskTitle_Position != -1:
                    Task_DB_Data.TaskDueDate[Old_TaskTitle_Position] = New_TaskDueDate
                    Task_DB_Data.TaskAssignedUser[Old_TaskTitle_Position] = New_AssignUser
                    Task_DB_Data.put()
                    TB_DB_Data.TaskConnect = Task_DB_Data
                    TB_DB_Data.put()
                    self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=TaskTitleAlreadyExistOtherDataEdited')

        elif self.request.get('SubmitButton') == 'Delete':
            TaskCount = len(Task_DB_Data.TaskTitle)
            if TaskCount > 1:
                del Task_DB_Data.TaskTitle[Old_TaskTitle_Position]
                del Task_DB_Data.TaskDueDate[Old_TaskTitle_Position]
                del Task_DB_Data.TaskAssignedUser[Old_TaskTitle_Position]
                del Task_DB_Data.TaskCompleteStatus[Old_TaskTitle_Position]
                del Task_DB_Data.TaskCompleteDate[Old_TaskTitle_Position]
                del Task_DB_Data.TaskCompleteTime[Old_TaskTitle_Position]
                Task_DB_Data.put()
                TB_DB_Data.TaskConnect = Task_DB_Data
                TB_DB_Data.put()
                self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=TaskDeletedSuccessfully')
            else:
                del Task_DB_Data.TaskTitle[Old_TaskTitle_Position]
                del Task_DB_Data.TaskDueDate[Old_TaskTitle_Position]
                del Task_DB_Data.TaskAssignedUser[Old_TaskTitle_Position]
                del Task_DB_Data.TaskCompleteStatus[Old_TaskTitle_Position]
                del Task_DB_Data.TaskCompleteDate[Old_TaskTitle_Position]
                del Task_DB_Data.TaskCompleteTime[Old_TaskTitle_Position]
                Task_DB_Data.put()
                Task_DB_Data.key.delete()
                del TB_DB_Data.TaskConnect.TaskTitle[Old_TaskTitle_Position]
                del TB_DB_Data.TaskConnect.TaskDueDate[Old_TaskTitle_Position]
                del TB_DB_Data.TaskConnect.TaskAssignedUser[Old_TaskTitle_Position]
                del TB_DB_Data.TaskConnect.TaskCompleteStatus[Old_TaskTitle_Position]
                del TB_DB_Data.TaskConnect.TaskCompleteDate[Old_TaskTitle_Position]
                del TB_DB_Data.TaskConnect.TaskCompleteTime[Old_TaskTitle_Position]
                TB_DB_Data.put()
                self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=LastTaskDeletedSuccessfully')

app = webapp2.WSGIApplication([
    ('/EditTask', EditTask),
], debug=True)
