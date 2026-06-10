from fastapi import APIRouter, Depends
from backend.schemas.number import NumberCheck
from backend.services.numverify import check_number
from backend.dependencies.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.logging import logger
from backend.models.check import NumberCheck as CheckModel
from backend.dependencies.db import get_redis
import redis.asyncio as redis
import json
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

router = APIRouter()


@router.post("/check")
async def check(
    number: NumberCheck,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    ext_number = number.number  # Extracting number from pydantic model
    cache_key = f'phone:v1:{ext_number}'
    data = None

    logger.info(f"Checking number {ext_number}")

    try:
        cached_val = await redis_client.get(cache_key)
        if cached_val:
            
            data = json.loads(cached_val)
            logger.info(f"Data retrieved from Redis for number {ext_number}")
            return data

    except Exception as e:
        logger.warning(f"Error while fetching data from Redis: {e}")

    result_from_db = None
    
    if not data:
        time_ago = datetime.now(timezone.utc) - timedelta(days=10)
        query = (
            select(CheckModel)
            .where(CheckModel.number == ext_number, CheckModel.created_at > time_ago)
            .order_by(CheckModel.created_at.desc())
            .limit(1)
        )
        result_db_check = await db.execute(query)
        result_from_db = result_db_check.scalar_one_or_none()

    if result_from_db:
        data = {
            "valid": result_from_db.is_valid,
            "number": result_from_db.number,
            "country_name": result_from_db.country,
            "country_code": result_from_db.country_code,
            "carrier": result_from_db.carrier,
            "line_type": result_from_db.type,
            "local_format": result_from_db.local_format,
        }
        
        # Check how old is the check
        expiration_date = result_from_db.created_at + timedelta(days=10)
        remaining_time = expiration_date - datetime.now(timezone.utc)

        ttl_seconds = int(remaining_time.total_seconds())

        # Save to redis if still valid
        if ttl_seconds > 0:
            try:
                await redis_client.setex(
                    cache_key,
                    ttl_seconds,
                    json.dumps(data)
                )
                logger.info(f"Result for number {ext_number} from DB saved to Redis")

            except Exception as e:
                logger.warning(f"Error while saving data to Redis: {e}")

        logger.info(f"Data requested from DB for number {ext_number}")
        return data

    if not data:
        data = await check_number(ext_number)

        logger.info(f"Externall API call made for number {ext_number}")

        try:
            await redis_client.setex(
                cache_key,
                timedelta(days=10),
                json.dumps(data)
            )

            logger.info(f'Result for number {ext_number} saved to Redis')

        except Exception as e:
            logger.warning(f"Error while saving data to Redis for number: {e}")

    new_record = CheckModel(
        is_valid=data.get("valid"),
        number=data.get("number"),
        country=data.get("country_name"),
        country_code=data.get("country_code"),
        carrier=data.get("carrier"),
        type=data.get("line_type"),
        local_format=data.get("local_format"),
    )

    print(new_record)
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)

    logger.info(f"Record was created for number {ext_number}")
    return new_record
