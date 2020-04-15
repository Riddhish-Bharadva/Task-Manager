from google.appengine.ext import ndb

class TaskDB(ndb.Model):
    TaskTitle = ndb.StringProperty(repeated=True)
    TaskDueDate = ndb.StringProperty(repeated=True)
    TaskAssignedUser = ndb.StringProperty(repeated=True)
    TaskCompleteStatus = ndb.IntegerProperty(repeated=True)
    TaskCompleteDate = ndb.StringProperty(repeated=True)
    TaskCompleteTime = ndb.StringProperty(repeated=True)
