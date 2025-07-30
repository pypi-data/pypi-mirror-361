import sys

from fastapi import FastAPI
from fastapi import __version__ as fastapi_version
from fastapi.staticfiles import StaticFiles

from src.core.config import config

app = FastAPI(
    debug=config.DEBUG_MODE,
    docs_url=None,  # 关闭 Swagger UI
    redoc_url=None,  # 关闭 ReDoc UI
)
app.mount(
    config.STATIC_URL,
    StaticFiles(directory=config.STATIC_DIR),
    name=config.STATIC_NAME,
)


@app.get("/server-status", include_in_schema=False)
async def server_status():
    data = {
        "server_status": "running",
        "fastapi_version": fastapi_version,
        "python_version": sys.version_info,
    }
    return data
