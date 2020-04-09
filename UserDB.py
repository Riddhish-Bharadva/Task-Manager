from google.appengine.ext import ndb

class UserDB(ndb.Model):
    user_Email = ndb.StringProperty()
