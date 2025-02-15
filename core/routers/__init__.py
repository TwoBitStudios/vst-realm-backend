from .user import router as user_router
from .comment import router as comment_router
from .replies import router as replies_router
from .comment_vote import router as comment_vote_router
from .product import router as product_router
from .auth.base import router as base_auth_router
from .auth.local import router as local_auth_router
from .auth.google import router as google_auth_router
