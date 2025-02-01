from contextlib import asynccontextmanager

from beanie import Document, init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from core import models, routers
from core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):

    client = AsyncIOMotorClient(settings.MONGODB_READ_URL)
    await init_beanie(
        database=client[settings.MONGODB_DATABASE], document_models=[models.User, models.Comment, models.Product]
    )

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CSRF_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(routers.user.router, prefix='/user')
