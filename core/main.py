from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient

from core import (
    PROJECT_VERSION,
    models,
    routers,
)
from core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(settings.MONGODB_READ_URL)
    await init_beanie(
        database=client[settings.MONGODB_DATABASE],
        document_models=[models.PrivateUser, models.Account, models.Comment, models.Product]
    )

    yield


templates = Jinja2Templates(directory='core/templates')

app = FastAPI(
    lifespan=lifespan,
    title='VST Realm API',
    version=PROJECT_VERSION,
    docs_url=None,
    redoc_url='/redoc/',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CSRF_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get('/docs/', include_in_schema=False, response_class=HTMLResponse)
async def get_docs_ui(request: Request):
    return templates.TemplateResponse(
        request,
        name='elements.html',
        context={
            'title': app.title,
            'api_description_url': app.openapi_url
        },
    )


@app.get('/auth/exists/')
async def check_email_exists(email: str) -> dict:
    user = await models.PrivateUser.find_one(models.PrivateUser.email == email)
    exists = user is not None
    is_local = bool(user.password) if exists else False

    return {
        'exists': exists,
        'is_local': is_local,
    }


app.include_router(routers.user_router, prefix='/user')
app.include_router(routers.comment_router, prefix='/comment')
app.include_router(routers.product_router, prefix='/product')
app.include_router(routers.local_auth_router, prefix='/auth/local')
app.include_router(routers.google_auth_router, prefix='/auth/google')
