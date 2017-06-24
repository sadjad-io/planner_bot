from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Session = sessionmaker()

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer , primary_key=True)
    user_id = Column(Integer)
    fname = Column(String(128))
    lname = Column(String(128))
    username = Column(String(128))
    user_lvl = Column(Integer)
    
class Events(Base):
    __tablename__ = 'events'

    id = Column(Integer , primary_key=True)
    owner_id = Column(Integer)
    title = Column(String(128))
    description = Column(String(1024))
    agree_users = Column(String)

engine = create_engine('sqlite:///planner.db')
Base.metadata.create_all(engine)
Session.configure(bind=engine)

session = Session()

'''
Decorator : Check User States
'''
def user(f):
    def check_user(message):
        result = session.query(Users).filter_by(user_id=message.chat.id).first()
        if result:
            return True
        else:
            user = Users(user_id = message.chat.id , fname = message.chat.first_name , lname = message.chat.last_name , username = message.chat.username , user_lvl = 0)
            session.add(user)
            session.commit()
            return True
    def decorator(message):
            check_user(message)
            f(message)
    return decorator
    
def command(f):
    def check_lvl(message):
        result = session.query(Users).filter_by(user_id=message.chat.id).first()
        if result:
            return result.user_lvl
        else:
            return False
    def decorator(message):
            check_lvl(message)
            f(message)
    return decorator