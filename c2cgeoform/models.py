from sqlalchemy import Column, Integer, LargeBinary, Text
from .ext import colander_ext

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from zope.sqlalchemy import register

DBSession = scoped_session(sessionmaker())
register(DBSession)
Base = declarative_base()


class FileData():
    id = Column(Integer, primary_key=True)
    filename = Column(Text, nullable=True)
    data = Column(LargeBinary, nullable=False, info={
        'colanderalchemy': {
            'typ': colander_ext.BinaryData()
        }})
