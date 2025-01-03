# apis/routes.py
from fastapi import APIRouter
from apis import webhook, channel, status

api_router = APIRouter()
api_router.include_router(webhook.router, tags=["webhooks"])
api_router.include_router(channel.router, tags=["channels"])
api_router.include_router(status.router, tags=["system"])