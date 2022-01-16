from fastapi import Header, HTTPException, status


def multipart_form_data(content_type: str = Header(...)):
    """Force request MIME-type to multipart/form-data"""

    if content_type != "multipart/form-data":
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported media type: {content_type}."
            " It must be multipart/form-data",
        )
