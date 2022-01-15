from typing import Any, Dict, Union
from sqlalchemy.orm import Session
from climbing.models import Route
from climbing.schemas.route import RouteCreate, RouteUpdate
from .base import CRUDBase


class CRUDRoute(CRUDBase[Route, RouteCreate, RouteUpdate]):
    """CRUD class for route models"""

    def create(self, database: Session, entity: RouteCreate) -> Route:
        print(entity)

    def update(
        self,
        database: Session,
        *,
        db_entity: Route,
        new_entity: Union[RouteUpdate, Dict[str, Any]],
    ) -> Route:
        print(f"Old: {db_entity}\nNew: {new_entity}")


route = CRUDRoute(Route)
