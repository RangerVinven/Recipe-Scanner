from pydantic import BaseModel

class GenerateRecipe(BaseModel):
    recipe_url: str
