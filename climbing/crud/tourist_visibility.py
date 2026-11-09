"""SQL-условия видимости трасс и подъёмов."""

from sqlalchemy import select, true
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import col

from climbing.db.models.ascent import Ascent
from climbing.db.models.route import Route
from climbing.db.models.user import User


def visible_route_clause(include_tourists: bool) -> ColumnElement[bool]:
    if include_tourists:
        return true()
    return col(Route.author_id).in_(
        select(User.id).where(col(User.is_tourist).is_(False))
    )


def visible_ascent_clause(include_tourists: bool) -> ColumnElement[bool]:
    if include_tourists:
        return true()
    return col(Ascent.user_id).in_(
        select(User.id).where(col(User.is_tourist).is_(False))
    ) & col(Ascent.route_id).in_(
        select(Route.id).where(visible_route_clause(include_tourists=False))
    )
