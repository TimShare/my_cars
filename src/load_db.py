import csv
import asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from infrastructure.models import Brand, Model, Car
from core.entites.car import (
    FuelType,
    TransmissionType,
    DriveType,
    CarCondition,
)
from settings import get_settings

settings = get_settings()
# Замените URL на асинхронный
DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
print(f"Подключение к базе данных: {DATABASE_URL}")

async_engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    class_=AsyncSession, autocommit=False, autoflush=False, bind=async_engine
)


async def populate_database(csv_file):
    async with AsyncSessionLocal() as db:
        try:
            with open(csv_file, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                brands_cache = {}
                models_cache = {}

                for row in reader:
                    print(row)
                    brand_name = row["brand_name"]
                    if brand_name not in brands_cache:
                        # Асинхронный запрос к БД
                        result = await db.execute(
                            Brand.__table__.select().where(Brand.name == brand_name)
                        )
                        brand = result.scalars().first()

                        if not brand:
                            brand = Brand(
                                id=uuid4(),
                                name=brand_name,
                                country=row["brand_country"],
                                logo_url=row["brand_logo_url"],
                            )
                            db.add(brand)
                            await db.commit()
                            await db.refresh(brand)
                        brands_cache[brand_name] = brand.id
                    brand_id = brands_cache[brand_name]

                    model_name = row["model_name"]
                    model_key = (
                        str(brand_id),
                        model_name,
                    )  # Преобразуем UUID в строку для ключа
                    if model_key not in models_cache:
                        # Асинхронный запрос к БД
                        result = await db.execute(
                            Model.__table__.select().where(
                                Model.brand_id == brand_id, Model.name == model_name
                            )
                        )
                        model = result.scalars().first()

                        if not model:
                            model = Model(
                                id=uuid4(),
                                brand_id=brand_id,
                                name=model_name,
                                year_from=(
                                    int(row["model_year_from"])
                                    if row["model_year_from"]
                                    else None
                                ),
                                year_to=(
                                    int(row["model_year_to"])
                                    if row["model_year_to"]
                                    else None
                                ),
                            )
                            db.add(model)
                            await db.commit()
                            await db.refresh(model)
                        models_cache[model_key] = model.id
                    model_id = models_cache[model_key]

                    car = Car(
                        id=uuid4(),
                        model_id=model_id,
                        year=int(row["car_year"]),
                        price=float(row["car_price"]),
                        mileage=int(row["car_mileage"]),
                        condition=CarCondition(row["car_condition"]),
                        fuel_type=FuelType(row["car_fuel_type"]),
                        transmission=TransmissionType(row["car_transmission"]),
                        drive_type=DriveType(row["car_drive_type"]),
                        color=row["car_color"] if row["car_color"] else None,
                        engine_volume=(
                            float(row["car_engine_volume"])
                            if row["car_engine_volume"] != "null"
                            and row["car_engine_volume"]
                            else None
                        ),
                        power=int(row["car_power"]) if row["car_power"] else None,
                        description=(
                            row["car_description"] if row["car_description"] else None
                        ),
                        vin=row["car_vin"] if row["car_vin"] else None,
                        photos=(
                            row["car_photos"].split(";") if row["car_photos"] else []
                        ),
                        is_sold=False,
                    )
                    db.add(car)
                    # Коммитим каждую машину, чтобы не держать большую транзакцию
                    await db.commit()

        except Exception as e:
            await db.rollback()
            print(f"Произошла ошибка: {e}")
            raise e


async def main():
    try:
        await populate_database("/Users/timursarafiev/Documents/to_cars_db.csv")
        print("База данных успешно заполнена!")
    except Exception as e:
        print(f"Произошла ошибка при загрузке данных: {e}")


if __name__ == "__main__":
    asyncio.run(main())
