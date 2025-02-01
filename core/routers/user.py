from beanie import Document, init_beanie
from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorClient

from core import models
from core.settings import settings

router = APIRouter()
client = AsyncIOMotorClient(settings.MONGODB_READ_URL)


@router.get('/users/', tags=['users'])
async def list_users():
    await init_beanie(database=client[settings.MONGODB_DATABASE], document_models=[models.User])
