import os
import sqlalchemy
import uvicorn

from .database.defaults import DEFAULT_DATABASE_NAME, DEFAULT_DATABASE_USERNAME
from .routes import WishRoutes
from .tags.metadata import tags_metadata

from contextlib import asynccontextmanager
from databases import Database
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

# global variables
database: Database
database_url: str
metadata = sqlalchemy.MetaData()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global database
    global database_url
    global metadata
    await database.connect()

    engine = create_async_engine(database_url, echo=True)

    async with engine.connect() as conn:
        await conn.run_sync(metadata.create_all)

    yield
    
    await database.disconnect()
    await engine.dispose()
    database = None
    engine = None
    metadata = None

database_type: str = os.environ["DATABASE_TYPE"]

if database_type in [ "mysql", "pgsql" ]:
    database_host = os.environ.get("DATABASE_HOST", None)
    database_name = os.environ.get("DATABASE_NAME", DEFAULT_DATABASE_NAME)
    database_password = os.environ.get("DATABASE_PASSWORD", None)
    database_port = os.environ.get("DATABASE_PORT", None)
    database_user = os.environ.get("DATABASE_USER", DEFAULT_DATABASE_USERNAME)
    if database_type == "mysql":
        database_url = f"mysql+aiomysql://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}"

    database = Database(database_url)

wish_routes = WishRoutes(database = database, metadata = metadata)

app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata)
app.include_router(wish_routes.router)

@app.get("/readiness")
async def readiness():
    return {"status": "ok"}

def start():
    """Launched with `poetry run start` at root level"""
 
    try:
        uvicorn.run("wishlist_backend.main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as ex:
        print(str(ex))