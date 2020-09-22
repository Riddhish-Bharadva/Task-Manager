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
        TaskBoard_ID = self.request.get('id') # Getting taskboard name from URL.
        Old_TaskTitle = self.request.get('tasktitle') # Getting taskname from taskboard page.
        # Declaration of required variables starts here.
        RequiredTaskData = []
        TBData = ''
        # Declaration of required variables ends here.

        if userLoggedIn: # Checking if user is logged in or not.
            loginLink = users.create_logout_url(self.request.uri)
            loginStatus = 'Logout'
            user_Key = ndb.Key('UserDB', userLoggedIn.email()).get()
            TBData = ndb.Key('TaskBoardDB',TaskBoard_ID).get()
            TaskData = ndb.Key('TaskDB', TaskBoard_ID).get() # Fetching task data for given taskboard.
            if TaskData != None: # If there are task data for given taskboard in TaskDB, fetch below data.
                # I am fetching task data from DB to send it to html page to display in text boxes.
                for i in range(0, len(TaskData.TaskTitle)):
                    if TaskData.TaskTitle[i] == Old_TaskTitle:
                        RequiredTaskData.append(TaskData.TaskTitle[i])
                        RequiredTaskData.append(TaskData.TaskDueDate[i])
                        RequiredTaskData.append(TaskData.TaskAssignedUser[i])
        else: # If user is not logged in, redirect user to home page.
            loginLink = users.create_login_url(self.request.uri)
            loginStatus = 'Login'
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
        # Fetching all data from EditTask.html page.
        TaskBoard_ID = self.request.get('id')
        Old_TaskTitle = self.request.get('Old_TaskTitle')

        New_TaskTitle = self.request.get('TaskTitleTB')
        New_TaskDueDate = self.request.get('TaskDueDate')
        New_TaskDueDate = datetime.strptime(New_TaskDueDate,'%Y-%m-%d')
        New_AssignUser = self.request.get('SelectToAssignUser')
        #Fetching data ends.

        TB_DB_Data = ndb.Key('TaskBoardDB',TaskBoard_ID).get()
        Task_DB_Data = ndb.Key('TaskDB', TaskBoard_ID).get()
        Old_TaskTitle_Position = -1 # Initializing position of task variable.
        for i in range(0,len(Task_DB_Data.TaskTitle)):
            if Task_DB_Data.TaskTitle[i] == Old_TaskTitle:
                Old_TaskTitle_Position = i
                break

        if self.request.get('SubmitButton') == 'Edit':
            New_TaskTitle_Match_Found = 0
            # Below for loop checks if new taskname entered by user already exist in TaskDB or not.
            for i in range(0,len(Task_DB_Data.TaskTitle)):
                if Task_DB_Data.TaskTitle[i] == New_TaskTitle:
                    New_TaskTitle_Match_Found = 1
                    break
            if New_TaskTitle_Match_Found == 0: # In case new task name is not present, existing old taskname will be updated.
                if Old_TaskTitle_Position != -1: # If old taskname is found, then proceed as below.
                    Task_DB_Data.TaskTitle[Old_TaskTitle_Position] = New_TaskTitle
                    Task_DB_Data.TaskDueDate[Old_TaskTitle_Position] = New_TaskDueDate
                    Task_DB_Data.TaskAssignedUser[Old_TaskTitle_Position] = New_AssignUser
                    Task_DB_Data.put()
                    # In below 3 lines, I am putting new task data in taskboard database. This is because my TaskBoardDB holds name of tasks every taskboard contains.
                    TB_DB_Data.TaskConnect = Task_DB_Data
                    TB_DB_Data.put()
                    self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=TaskDataEditedSuccessfully')
            else:
                if Old_TaskTitle_Position != -1: # In case task with same name already exist, just update other fields like Assigned user and task due date for existing task.
                    Task_DB_Data.TaskDueDate[Old_TaskTitle_Position] = New_TaskDueDate
                    Task_DB_Data.TaskAssignedUser[Old_TaskTitle_Position] = New_AssignUser
                    Task_DB_Data.put()
                    # Updating data in TaskBoardDB as well in below lines.
                    TB_DB_Data.TaskConnect = Task_DB_Data
                    TB_DB_Data.put()
                    self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=TaskTitleAlreadyExistOtherDataEdited')

        elif self.request.get('SubmitButton') == 'Delete':
            TaskCount = len(Task_DB_Data.TaskTitle)
            if TaskCount > 1: # In case number of tasks in TaskBoard are more than 1, delete only required task from list.
                del Task_DB_Data.TaskTitle[Old_TaskTitle_Position]
                del Task_DB_Data.TaskDueDate[Old_TaskTitle_Position]
                del Task_DB_Data.TaskAssignedUser[Old_TaskTitle_Position]
                del Task_DB_Data.TaskCompleteStatus[Old_TaskTitle_Position]
                del Task_DB_Data.TaskCompleteDate[Old_TaskTitle_Position]
                del Task_DB_Data.TaskCompleteTime[Old_TaskTitle_Position]
                Task_DB_Data.put()
                # Below lines updates data in TaskBoardDB.
                TB_DB_Data.TaskConnect = Task_DB_Data
                TB_DB_Data.put()
                self.redirect('/TaskBoardData?id='+TaskBoard_ID+'&notification=TaskDeletedSuccessfully')
            else: # In case number of tasks in TaskBoard is 1, delete the whole record along with Key from TaskDB table.
                del Task_DB_Data.TaskTitle[Old_TaskTitle_Position]
                del Task_DB_Data.TaskDueDate[Old_TaskTitle_Position]
                del Task_DB_Data.TaskAssignedUser[Old_TaskTitle_Position]
                del Task_DB_Data.TaskCompleteStatus[Old_TaskTitle_Position]
                del Task_DB_Data.TaskCompleteDate[Old_TaskTitle_Position]
                del Task_DB_Data.TaskCompleteTime[Old_TaskTitle_Position]
                Task_DB_Data.put()
                Task_DB_Data.key.delete()
                # Below lines deletes data from TaskBoardDB as well.
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
