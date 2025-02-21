from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class NewsLog(Base):

    __tablename__ = 'news_logs'

    id = Column(Integer, primary_key=True)
    author = Column(String, nullable=False)
    title = Column(String, nullable=False)
    urlToImage = Column(String, nullable=True)
    category = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)