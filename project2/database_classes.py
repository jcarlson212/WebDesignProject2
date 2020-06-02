from sqlalchemy import Column, Integer, String, MetaData, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import create_engine
import os

Base = declarative_base()

class Channel(Base):
    __tablename__ = 'Channels'
    id = Column(String, primary_key=True)
    def __repr__(self):
        return "%s" % self.id

class Message(Base):
    __tablename__ = 'Messages'
    id = Column(Integer, primary_key=True) #aut-increments by default
    userPosted = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    def __repr__(self):
        return "%s %s %s %s %s" % (self.id, self.userPosted, self.channel, self.message, self.timestamp.toString())

#os.environ.get('DB_PATH')
db = create_engine('postgres://hnulgvbhhhvrrn:2843c3b5f049942b975a6ca1ecb098caeaadd58c90c4e1d75b7e5bdb07d1cd06@ec2-23-22-156-110.compute-1.amazonaws.com:5432/d911g27f2j67g7')

Base.metadata.create_all(db)