from sqlalchemy.orm import Session
from fastapi import Header, status, HTTPException
from db.session import SessionLocal


def get_database() -> Session:
    """Creates new connection to database and automatically closes it after
    using

    Yields:
        [Session]: database connection
    """

    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


def multipart_form_data(content_type: str = Header(...)):
    """Force request MIME-type to multipart/form-data"""

    if content_type != "multipart/form-data":
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported media type: {content_type}."
            " It must be multipart/form-data",
        )
