from pydantic import BaseModel
from typing import Optional

class GenerateRecipe(BaseModel):
    recipe_url: str

class RecipeOptionalAttributes(BaseModel):
    Servings: Optional[int] = None
    Cook_Time_In_Minutes: Optional[int] = None
    Calories: Optional[int] = None
    Carbs: Optional[int] = None
    Protein: Optional[int] = None
    Fats: Optional[int] = None
    Sugars: Optional[int] = None
    Recipe_URL: Optional[str] = None

class CreateRecipe(RecipeOptionalAttributes):
    Recipe_Name: str

class UpdateRecipe(RecipeOptionalAttributes):
    Recipe_Name: Optional[str] = None
