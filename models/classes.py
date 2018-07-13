
from mongoengine import *

class User(Document):
    username = StringField(unique=True)
    email = StringField(unique= True)
    password = StringField()


class Topic(Document):
    question = StringField()
    group = StringField()
    image = StringField()
    accepted = BooleanField(default = False)
    votes_yes = IntField(default = 0)
    votes_no = IntField(default = 0)
    users_voted = ListField(StringField())
    author = StringField()

class Vote(Document):
    user = StringField()
    topic = ReferenceField(Topic)
    answer =  StringField()
    vote_yes = BooleanField()
    reported = BooleanField(default = False)
