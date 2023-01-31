import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from main import app, get_db

TEST_DATABASE_URL = 'sqlite+aiosqlite:///./test.db'

engine = create_async_engine(TEST_DATABASE_URL)
test_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def override_get_db():
    try:
        db = test_session()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_all_recipes():
    response = client.get('/recipes/')

    assert response.json() == [
        {'name': 'Glass of water', 'cooking_time': 0, 'views_count': 0},
        {'name': 'Sandwich', 'cooking_time': 2, 'views_count': 0}
    ]


@pytest.mark.asyncio
async def test_list_of_recipes_sorting():
    client.get('/recipes/2')

    response = client.get('/recipes/')

    assert response.json() == [
        {'name': 'Sandwich', 'cooking_time': 2, 'views_count': 1},
        {'name': 'Glass of water', 'cooking_time': 0, 'views_count': 0}
    ]


@pytest.mark.asyncio
async def test_get_one_recipe():
    response = client.get('/recipes/1')

    assert response.json() == {
        "name": "Glass of water",
        "cooking_time": 0,
        "ingredients": ["Water"],
        "description": "Just put some water into the glass"
    }
