from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class TwitterUser(Base):
    __tablename__ = "twitter_user"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    screen_name = Column(String(50), nullable=False)
    description = Column(String(160))


class TwitterConnection(Base):
    __tablename__ = 'twitter_connection'

    id = Column(Integer, primary_key=True)
    from_user_id = Column(ForeignKey("twitter_user.id"))
    from_user = relationship("TwitterUser", foreign_keys=[from_user_id])
    to_user_id = Column(ForeignKey("twitter_user.id"))
    to_user = relationship("TwitterUser", foreign_keys=[to_user_id])
