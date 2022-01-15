from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api_v1.api import api_router
from core.config import settings

app = FastAPI(
    contact={
        "Автор": "Александр Макурин ae_mc@mail.ru|alexandr.mc12@gmail.com"
    },
)

app.include_router(api_router, prefix=settings.API_V1_STR)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.post("/test")
# def test(
#     model: SomeModel = Body(
#         ...,
#         description="Должна передаваться в виде строки, которая в"
#         " дальнейшем парситься в JSON-объект с помощью json.loads."
#         " Для более подробного описания см. **SomeModel**.",
#     ),
#     token: str = Depends(auth_schema),
# ):
#     """Function for testing purposes"""
#     return f"Ok. Id is {model.id}. Token's value is '{token}'"
