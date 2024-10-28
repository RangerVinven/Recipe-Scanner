from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import select, insert, update, delete

from models.tables import recipes_table, ingredients_table
from models.ingredients import CreateIngredients, UpdateIngredients

from utils.request_manager import get_user_id
from utils.database_connector import connection
from utils.query_manager import join_tables_query

ingredients_router = APIRouter(prefix="/ingredients")

def authorise_request(user_id, recipe_id):
    # Checks if the user owns the recipe
    select_query = select(recipes_table).where(recipes_table.c.Recipe_ID == recipe_id).where(recipes_table.c.User_ID == user_id)
    results = connection.execute(select_query).mappings().all()

    # If the user doesn't own the recipe
    if len(results) == 0:
        raise HTTPException(status_code=404)

# Returns all the steps for a given recipe
@ingredients_router.get("/{recipe_id}")
def get_ingredients(recipe_id: int, request: Request):
    user_id = get_user_id(request)

    # Runs the select query
    recipes_steps_join = join_tables_query(ingredients_table, ingredients_table.c.Recipe_ID, recipes_table, recipes_table.c.Recipe_ID)
    select_query = select(ingredients_table).select_from(recipes_steps_join).where(recipes_table.c.Recipe_ID == recipe_id).where(recipes_table.c.User_ID == user_id)
    results = connection.execute(select_query).mappings().all() # mappings... turns the result into JSON

    return results

@ingredients_router.post("/{recipe_id}")
def create_ingredients(ingredients: CreateIngredients, request: Request, recipe_id: int):
    user_id = get_user_id(request)
    authorise_request(user_id, recipe_id)

    # Ensures there's at least one ingredient
    if len(ingredients.Ingredients) == 0:
        raise HTTPException(status_code=400)

    # Turns the ingredients into a pure JSON object (no custom objects)
    ingredients = [dict(ingredient) for ingredient in ingredients.Ingredients]

    # Adds the recipe_id to each of the objects in the ingredients array
    recipe_id_json = {"Recipe_ID": recipe_id}
    ingredients = [{**recipe_id_json, **ingredient} for ingredient in ingredients]

    # Inserts the ingredients
    insert_query = insert(ingredients_table).values(ingredients)
    results = connection.execute(insert_query)
    connection.commit()

    # If the ingredients weren't inserted weren't
    if results.rowcount == 0:
        raise HTTPException(status_code=500)

    return

@ingredients_router.put("/{recipe_id}")
def update_ingredients(recipe_id: int, request: Request, ingredients: UpdateIngredients):
    user_id = get_user_id(request)
    authorise_request(user_id, recipe_id)

    # Loops through the steps and updates them
    for ingredient in ingredients.Ingredients:
        ingredients = dict(ingredient)

        update_query = update(ingredients_table).where(ingredients_table.c.Ingredient_ID == ingredient["Ingredient_ID"]).where(ingredients_table.c.Recipe_ID == recipe_id).values(ingredient)
        connection.execute(update_query)

    connection.commit()
    return

@ingredients_router.delete("/{ingredient_id}")
def delete_step(ingredient_id: int, request: Request):
    user_id = get_user_id(request)

    # Gets the recipe_id to be able to check if the user owns the recipe
    select_query = select(ingredients_table).where(ingredients_table.c.Ingredient_ID == ingredient_id)
    result = connection.execute(select_query).first()

    if len(result) == 0:
        raise HTTPException(status_code=404)

    print(result)
    authorise_request(user_id, result[4])

    # Deletes the step
    delete_query = delete(ingredients_table).where(ingredients_table.c.Ingredient_ID == ingredient_id)
    results = connection.execute(delete_query)
    connection.commit()

    # If nothing was deleted
    if results.rowcount == 0:
        raise HTTPException(status_code=500)

    return
