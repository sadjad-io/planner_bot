# -*- coding: utf-8 -*-

from sqlalchemy import *
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import config

Base = declarative_base()
engine = create_engine('sqlite:///planner.db?check_same_thread=False')

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer , primary_key=True)
    user_id = Column(Integer)
    fname = Column(String(128))
    lname = Column(String(128))
    username = Column(String(128))
    user_lvl = Column(String)

class Events(Base):
    __tablename__ = 'events'

    id = Column(Integer , primary_key=True)
    owner_id = Column(String(128))
    title = Column( String(128) , server_default= u"وارد نشده" )
    description = Column(String(1024) , server_default= u"وارد نشده")
    text = Column(Text , server_default= u"وارد نشده")
    agree_users = Column(Text)
    disagree_users = Column(Text)

Base.metadata.create_all(engine)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()

'''
Decorator : Check User States
'''
def user(function):
    def check_user(message):
        result = session.query(Users).filter_by(user_id=message.chat.id).first()
        if result:
            return True
        else:
            user = Users(user_id = message.chat.id , fname = message.chat.first_name , lname = message.chat.last_name , username = message.chat.username , user_lvl = "start")
            session.add(user)
            session.commit()
            return True
    def decorator(message):
            check_user(message)
            function(message)
    return decorator

def command(function):
    def check_message(message):
        if( message.text in config.commands ):
            return True
        else:
            return False

    def check_lvl(message):
        if( message.text in config.commands ):
            return True
        else:
            return False

    def set_lvl(message,f_name):
        user = session.query(Users).filter_by(user_id=message.chat.id).first()
        user.user_lvl = f_name.__name__
        session.commit()
    def decorator(message):
            set_lvl(message,function)
            if( check_lvl(message) ):
                pass
            else:
                function(message)
    return decorator
