import logging
import os

from beanie import init_beanie
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from .models import Ptt

load_dotenv()

DATABASE_NAME = "Crawler"
MONGODB_CONNECTION_URL = os.getenv("MONGODB_CONNECTION_URL")


async def init_db():
    client = AsyncIOMotorClient(MONGODB_CONNECTION_URL)

    await init_beanie(database=client[DATABASE_NAME], document_models=[Ptt])

    logging.info("Database initialized successfully")


__all__ = ['init_db']
