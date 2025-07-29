from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING

from . import MilData, _ops, DB_NAME
from ..common.db_ops import get_collection

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "mil"


async def save(mil_data: MilData, client: AsyncIOMotorClient) -> dict:
    return await _ops.save(COL_NAME, mil_data, client)


async def save_many(many_data: dict[str, MilData], client: AsyncIOMotorClient) -> dict:
    return await _ops.save_many(COL_NAME, many_data, client)


async def get_latest(code: str, client: AsyncIOMotorClient) -> MilData | None:
    collection = get_collection(client, DB_NAME, COL_NAME)
    doc = await collection.find_one(
        {"코드": code},
        sort=[("날짜", DESCENDING)]
    )

    if doc:
        doc["_id"] = str(doc["_id"])
        mylogger.debug(doc)
        return MilData(**doc)
    else:
        mylogger.warning(f"데이터 없음: {code}")
        return None

