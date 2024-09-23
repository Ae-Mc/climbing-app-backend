from os import mkdir, path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_versionizer import Versionizer

from climbing.api.api_v1 import api_router as api_v1_router
from climbing.api.api_v2 import api_router as api_v2_router
from climbing.core.config import settings

app = FastAPI(
    contact={"Автор": "Александр Макурин ae_mc@mail.ru|alexandr.mc12@gmail.com"},
    version="v1",
)

app.include_router(api_v1_router)

if not path.exists("media"):
    mkdir("media")
static = StaticFiles(directory=settings.MEDIA_ROOT)
app.include_router(api_v2_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Versionizer(
    app=app,
    prefix_format="/api/v{major}",
    semantic_version_format="{major}",
    sort_routes=True,
    include_version_docs=True,
    include_versions_route=True,
).versionize()

app.mount("/media", static, name="media")
