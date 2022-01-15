from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import Header, status, HTTPException
from climbing.db.session import SessionLocal


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Creates new connection to database and automatically closes it after
    using

    Yields:
        [AsyncSession]: database connection
    """

    database = SessionLocal()
    try:
        yield database
    finally:
        await database.close()


def multipart_form_data(content_type: str = Header(...)):
    """Force request MIME-type to multipart/form-data"""

    if content_type != "multipart/form-data":
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported media type: {content_type}."
            " It must be multipart/form-data",
        )
