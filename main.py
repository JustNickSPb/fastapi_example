from fastapi import FastAPI, Path, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import engine, Base, async_session
import schemas

app = FastAPI()


async def get_db():
    db = async_session()
    try:
        yield db
    finally:
        await db.close()


@app.on_event("startup")
async def startapp():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown(session: AsyncSession = Depends(get_db)):
    await session.close()
    await engine.dispose()


async def make_good_recipe(recipe: models.Recipe) -> models.Recipe:
    """
    Extra action to normalize results from database.
    E.g., ingredients list that coming from db as list of Ingredient objects
    becomes list of ingredients as strings which seems to be better for app

    :param recipe: result from database
    :return: normalized result
    """
    rec = {'id': recipe.id,
           'name': recipe.name,
           'cooking_time': recipe.cooking_time,
           'description': recipe.description,
           'views_count': recipe.views_count,
           'ingredients': [ingr.product for ingr in recipe.ingredients]}

    return models.Recipe(**rec)


@app.get(
    '/recipes/',
    response_model=list[schemas.RecipeInList],
    summary='Get list of recipes',
    description='Get full list of recipes from database,'
                'sorted by their popularity descending and cooking time ascending.'
                'Each recipe info will include it\'s name, views count and cooking time in minutes.'
)
async def get_all_recipes(session: AsyncSession = Depends(get_db)) -> list[models.Recipe]:
    recipes_request = await session.execute(
        select(models.Recipe)
        .order_by(models.Recipe.views_count.desc())
        .order_by(models.Recipe.cooking_time)
    )
    recipes = recipes_request.scalars().all()
    return recipes


@app.get(
    '/recipes/{recipy_id}',
    response_model=schemas.RecipeDetailed,
    summary='Get detailed recipe info',
    description='Shows detailed info about exact recipe with given recipe_id.'
                'Includes name of the recipe, it\'s cooking time, list of needed ingredients '
                'and full description of cooking process'
)
async def get_one_recipy(
    session: AsyncSession = Depends(get_db),
    recipy_id: int = Path(title='Id of recipe to get')
) -> models.Recipe:
    recipy_request = await session.execute(select(models.Recipe)
                                           .filter(models.Recipe.id == recipy_id))
    recipy = recipy_request.scalars().first()
    recipy.views_count += 1
    await session.execute(update(models.Recipe)
                          .where(models.Recipe.id == recipy_id)
                          .values(views_count=recipy.views_count))
    await session.commit()
    result = await make_good_recipe(recipy)

    return result
