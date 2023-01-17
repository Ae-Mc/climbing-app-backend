from datetime import date

from fastapi import APIRouter, Body, Depends, Path
from fastapi_users_db_sqlmodel import AsyncSession
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError

import climbing.core.responses as responses
from climbing.core.security import current_active_user
from climbing.crud import competition as crud_competition
from climbing.db.models.competition import CompetitionCreate
from climbing.db.models.competition_participant import (
    CompetitionParticipantCreate,
)
from climbing.db.models.user import User
from climbing.db.session import get_async_session
from climbing.schemas.competition import CompetitionReadWithAll
from climbing.schemas.competition_participant import (
    CompetitionParticipantCreateScheme,
)

router = APIRouter()


@router.get("", response_model=list[CompetitionReadWithAll])
async def competitions(
    async_session: AsyncSession = Depends(get_async_session),
):
    """Получения списка всех соревнований"""
    return await crud_competition.get_all(session=async_session)


@router.post(
    "",
    response_model=CompetitionReadWithAll,
    responses={
        **responses.INTEGRITY_ERROR.docs(),
        **responses.UNAUTHORIZED.docs(),
    },
)
async def create_competition(
    name: str = Body(...),
    date: date = Body(...),  # pylint: disable=redefined-outer-name
    ratio: float = Body(...),
    participants: list[CompetitionParticipantCreateScheme] = Body(...),
    async_session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Добавление соревнования"""
    competition_create = CompetitionCreate(
        name=name,
        date=date,
        ratio=ratio,
        organizer_id=user.id,
        participants=participants,
    )
    try:
        return await crud_competition.create(async_session, competition_create)
    except IntegrityError as error:
        raise responses.INTEGRITY_ERROR.exception() from error


@router.post(
    "/{competition_id}/add_participant",
    responses={
        **responses.ID_NOT_FOUND.docs(),
        **responses.INTEGRITY_ERROR.docs(),
        **responses.UNAUTHORIZED.docs(),
    },
)
async def add_participant(
    competition_id: UUID4 = Path(...),
    participant: CompetitionParticipantCreateScheme = Body(...),
    async_session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Добавление участника к существующему соревнованию"""
    competition = await crud_competition.get(async_session, competition_id)
    if competition is None:
        raise responses.ID_NOT_FOUND.exception()
    if competition.organizer_id != user.id or not user.is_superuser:
        raise responses.UNAUTHORIZED.exception()
    try:
        return await crud_competition.add_participant(
            async_session,
            CompetitionParticipantCreate(
                **participant.dict(), competition_id=competition_id
            ),
        )
    except IntegrityError as error:
        raise responses.INTEGRITY_ERROR.exception() from error


@router.delete(
    "",
    response_model=CompetitionReadWithAll,
    responses={
        **responses.UNAUTHORIZED.docs(),
        **responses.ID_NOT_FOUND.docs(),
    },
)
async def delete_competition(
    competition_id: UUID4,
    async_session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Удаление соревнования"""
    competition = await crud_competition.get(async_session, competition_id)
    if competition is None:
        raise responses.ID_NOT_FOUND.exception()
    if competition.organizer_id != user.id and not user.is_superuser:
        raise responses.UNAUTHORIZED.exception()
    return await crud_competition.remove(async_session, row_id=competition_id)
