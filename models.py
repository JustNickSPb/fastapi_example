from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref

from database import Base


class Association(Base):
    __tablename__ = 'association_table'
    recipe_id = Column(Integer, ForeignKey('recipe_detail.id'), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredient.id'), primary_key=True)


class Recipe(Base):
    __tablename__ = 'recipe_detail'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    cooking_time = Column(Integer, index=True)
    description = Column(String)
    views_count = Column(Integer, default=0)
    ingredients = relationship('Ingredient',
                               secondary='association_table',
                               lazy='selectin')


class Ingredient(Base):
    __tablename__ = 'ingredient'
    id = Column(Integer, primary_key=True, index=True)
    product = Column(String, index=True)
    recipe = relationship('Recipe', secondary='association_table')
