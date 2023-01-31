import pytest_asyncio

from database import Base
from models import Recipe, Ingredient, Association
from test_main import test_session, engine


@pytest_asyncio.fixture(autouse=True)
async def fill_db():
    db = test_session()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with db as session:
        async with session.begin():
            session.add_all(
                [
                    Recipe(name='Glass of water',
                           cooking_time=0,
                           description='Just put some water into the glass'),
                    Recipe(name='Sandwich',
                           cooking_time=2,
                           description='Take a piece of bread and put anything onto it'),
                    Ingredient(product='Water'),
                    Ingredient(product='Bread'),
                    Ingredient(product='Cheese'),
                    Association(ingredient_id=1, recipe_id=1),
                    Association(ingredient_id=2, recipe_id=2),
                    Association(ingredient_id=3, recipe_id=2)
                ]
            )
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)