from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from climbing.db.base_class import Base

if TYPE_CHECKING:
    from climbing.models.file import File
    from climbing.models.route import Route


class RouteImage(Base):
    """Table for storing Route to image relationship"""

    route_id = Column(ForeignKey("route.id"), nullable=False)
    route: "Route" = relationship("Route", back_populates="images")
    image_id = Column(ForeignKey("file.id"), nullable=False)
    image: "File" = relationship("File")
