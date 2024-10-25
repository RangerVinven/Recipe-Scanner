from pydantic import BaseModel
from typing import List

class Ingredients(BaseModel):
    Ingredient_ID: int
    Ingredient_Name: str
    Ingredient_Amount: str
    Ingredient_Unit: str
    Recipe_ID: int

class Ingredient(BaseModel):
    Ingredient_Name: str
    Ingredient_Amount: str
    Ingredient_Unit: str

class IngredientWithID(Ingredient):
    Ingredient_ID: int

class CreateIngredients(BaseModel):
    Steps: List[Ingredient] = []

class UpdateIngredients(BaseModel):
    Steps: List[IngredientWithID] = []
