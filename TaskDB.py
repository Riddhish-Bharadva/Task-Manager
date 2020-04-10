from google.appengine.ext import ndb

class TaskDB(ndb.Model):
    TaskTitle = ndb.StringProperty()
    TaskDueDate = ndb.DateTimeProperty()
    TaskCompleteStatus = ndb.IntegerProperty()
