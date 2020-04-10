from google.appengine.ext import ndb
from TaskDB import TaskDB

class TaskBoardDB(ndb.Model):
    TBName = ndb.StringProperty()
    Admin_Email = ndb.StringProperty()
    TaskConnect = ndb.KeyProperty(TaskDB, repeated=True)
