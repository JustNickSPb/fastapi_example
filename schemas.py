from pydantic import BaseModel, Field


class BaseRecipe(BaseModel):
    name: str = Field(
        title='Name of recipe'
    )
    cooking_time: int = Field(
        title='Time in minutes needed to cook this dish'
    )

    class Config:
        orm_mode = True


class RecipeInList(BaseRecipe):
    views_count: int = Field(
        title='Shows how often was this recipe opened'
    )


class RecipeDetailed(BaseRecipe):
    ingredients: list[str] = Field(
        title='List of products needed to cook it'
    )
    description: str = Field(
        title='Full description of recipe'
    )
