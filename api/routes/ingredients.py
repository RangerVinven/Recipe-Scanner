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
def get_steps(recipe_id: int, request: Request):
    user_id = get_user_id(request)

    # Runs the select query
    recipes_steps_join = join_tables_query(ingredients_table, ingredients_table.c.Recipe_ID, recipes_table, recipes_table.c.Recipe_ID)
    select_query = select(ingredients_table).select_from(recipes_steps_join).where(recipes_table.c.Recipe_ID == recipe_id).where(recipes_table.c.User_ID == user_id)
    results = connection.execute(select_query).mappings().all() # mappings... turns the result into JSON

    return results

# @ingredients_router.post("/{recipe_id}")
# def create_steps(steps: CreateSteps, request: Request, recipe_id: int):
#     user_id = get_user_id(request)
#     authorise_request(user_id, recipe_id)
#
#     # Ensures there's at least one step
#     if len(steps.Steps) == 0:
#         raise HTTPException(status_code=400)
#
#     # Turns the steps into a pure JSON object (no custom objects)
#     steps = [dict(step) for step in steps.Steps]
#
#     # Adds the recipe_id to each of the objects in the steps array
#     recipe_id_json = {"Recipe_ID": recipe_id}
#     steps = [{**recipe_id_json, **step} for step in steps]
#
#     # Inserts the steps
#     insert_query = insert(steps_table).values(steps)
#     results = connection.execute(insert_query)
#     connection.commit()
#
#     # If the steps weren't inserted weren't
#     if results.rowcount == 0:
#         raise HTTPException(status_code=500)
#
#     return
#
# @ingredients_router.put("/{recipe_id}")
# def update_steps(recipe_id: int, request: Request, steps: UpdateSteps):
#     user_id = get_user_id(request)
#     authorise_request(user_id, recipe_id)
#
#     # Loops through the steps and updates them
#     for step in steps.Steps:
#         step = dict(step)
#
#         update_query = update(steps_table).where(steps_table.c.Step_ID == step["Step_ID"]).where(steps_table.c.Recipe_ID == recipe_id).values(step)
#         connection.execute(update_query)
#
#     connection.commit()
#
#
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
