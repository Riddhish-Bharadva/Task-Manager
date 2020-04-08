from google.appengine.ext import ndb

class User_DB(ndb.Model):
    user_Email = ndb.StringProperty()
