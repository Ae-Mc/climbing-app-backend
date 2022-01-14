from datetime import date

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType

from db.base_class import Base
from models.user import User


class File(Base):
    """Table for storing files"""

    url = Column(URLType, nullable=False)
    uploader_id = Column(ForeignKey("user.id"), nullable=False)
    uploader: User = relationship(User)
    created_at = Column(DateTime, default=date.today, nullable=False)
