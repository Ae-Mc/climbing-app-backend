from datetime import date

from sqlalchemy import Column, Date, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from climbing.db.base_class import Base
from climbing.models.route_image import RouteImage
from climbing.schemas import Category


class Route(Base):  # pylint: disable=too-few-public-methods
    """Table for storing routes"""

    name = Column(String(length=150), nullable=False)
    category = Column(Enum(Category), nullable=False)
    mark_color = Column(String(length=150), nullable=False)
    author = Column(String(length=150), nullable=False)
    uploader_id = Column(ForeignKey("user.id"), nullable=False)
    uploader = relationship("User", back_populates="routes")
    description = Column(String(length=2000), nullable=False)
    creation_date = Column(Date, default=date.today, nullable=False)
    images = relationship(
        "File",
        secondary=RouteImage.__tablename__,
        primaryjoin="Route.id == RouteImage.route_id",
        secondaryjoin="RouteImage.image_id == File.id",
        viewonly=True,
    )
