from fastapi import APIRouter, Depends
from backend.schemas.number import NumberCheck
from backend.services.numverify import check_number
from backend.dependencies.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.logging import logger
from backend.models.check import NumberCheck as CheckModel

router = APIRouter()


@router.post("/check")
async def check(
    number: NumberCheck,
    db: AsyncSession = Depends(get_db),
):
    ext_number = number.number  # Extracting number from pydantic model

    logger.info(f"Checking number {ext_number}")

    response = await check_number(ext_number)
    print(response)

    new_record = CheckModel(
        is_valid=response.get("valid"),
        number=response.get("number"),
        country=response.get("country_name"),
        country_code=response.get("country_code"),
        carrier=response.get("carrier"),
        type=response.get("line_type"),
        local_format=response.get("local_format"),
    )

    print(new_record)
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)

    logger.info(f"Record was created for number {ext_number}")
    return new_record
