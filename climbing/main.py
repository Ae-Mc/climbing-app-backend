from os import mkdir, path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from climbing.api.api_v1.api import api_router
from climbing.core.config import settings

app = FastAPI(
    contact={
        "Автор": "Александр Макурин ae_mc@mail.ru|alexandr.mc12@gmail.com"
    },
)

app.include_router(api_router, prefix=settings.API_V1_STR)

if not path.exists("media"):
    mkdir("media")
static = StaticFiles(directory=settings.MEDIA_ROOT)
app.mount("/media", static, name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
