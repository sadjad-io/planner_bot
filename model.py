from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Chat(Base):
    __tablename__ = 'chats'

    id = Column(Integer , primary_key=True)
    chat_id = Column(Integer)
    activate = Column(Boolean)

engine = create_engine('sqlite:///planner.db')
Base.metadata.create_all(engine)
