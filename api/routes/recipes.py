import os
import re
import json
import secrets
import requests
import urllib.request, urllib.error, urllib.parse

from time import sleep
from dotenv import load_dotenv

from sqlalchemy import insert, select, delete, update
from fastapi import APIRouter, HTTPException, Response, Request

from models.recipes import GenerateRecipe, CreateRecipe, UpdateRecipe
from models.tables import recipes_table, ingredients_table, steps_table

from utils.database_connector import connection
from utils.openai_connector import openai_client
from utils.query_manager import insert_data
from utils.request_manager import get_session_token, get_user_id

load_dotenv()

recipes_router = APIRouter(prefix="/recipes")

# Gets all the recipes belonging to a user
@recipes_router.get("/")
def get_recpies(request: Request):
    # Gets the user_id associated with the session token
    user_id = get_user_id(request)

    # Runs the select query
    select_query = select(recipes_table).where(recipes_table.c.User_ID == user_id)
    results = connection.execute(select_query)
    results_json = results.mappings().all()

    return results_json

# Gets a recipe
@recipes_router.get("/{recipe_id}")
def get_recipe(request: Request, recipe_id: int):

    # Gets the user_id associated with the session token
    user_id = get_user_id(request)

    # Selects the recipe with a matching user_id and recipe_id
    select_query = select(recipes_table).where(recipes_table.c.Recipe_ID == recipe_id).where(recipes_table.c.User_ID == user_id)
    results = connection.execute(select_query)
    results_json = results.mappings().all()

    # If the recipe exists
    if len(results_json) > 0:
        return results_json[0]

    raise HTTPException(status_code=404)


# Creates a recipe
@recipes_router.post("/")
def create_recipe(request: Request, recipe: CreateRecipe):
    # Gets the user_id and adds it to the recipe
    user_id = get_user_id(request)
    recipe_json = dict(recipe)
    recipe_json["User_ID"] = user_id

    recipe_id = insert_data(recipes_table, recipe_json)
    print(recipe_id)


    return

# Updates a recipe
@recipes_router.patch("/{recipe_id}")
def update_recipe(request: Request, recipe_id: int, recipe: UpdateRecipe):
    # Gets the user id
    user_id = get_user_id(request)
    
    # Changes removes the None values from the dictionary
    # Removes none values from the user's data,
    # Taken from: https://blog.finxter.com/5-best-ways-to-remove-null-values-from-a-python-dictionary/
    data = {k: v for k, v in vars(recipe).items() if v is not None}

    # Updates the recipe data
    update_query = update(recipes_table).where(recipes_table.c.Recipe_ID == recipe_id).where(recipes_table.c.User_ID == user_id).values(dict(data))
    results = connection.execute(update_query)
    connection.commit()

    # If the recipe doesn't exist, or if the user doesn't own it
    if results.rowcount == 0:
        raise HTTPException(status_code=404)

    return


# Deletes a recipe
@recipes_router.delete("/{recipe_id}")
def delete_recipe(request: Request, recipe_id: int):
    # Gets the user id
    user_id = get_user_id(request)

    # Attempts to delete the recipe 
    delete_query = delete(recipes_table).where(recipes_table.c.User_ID == user_id).where(recipes_table.c.Recipe_ID == recipe_id)
    results = connection.execute(delete_query)
    connection.commit()

    if results.rowcount == 0:
        raise HTTPException(status_code=404)

    return


# Uploads a file to OpenAI
async def upload_file(file_name):
    try:
        return openai_client.files.create(file=open("recipe_files/{}.html".format(file_name), "rb"), purpose="assistants")

    except: 
        raise HTTPException(status=500, detail="Couldn't upload recipe to OpenAI")

@recipes_router.post("/extract_recipe")
async def generate_recipe(recipe: GenerateRecipe, request: Request):
    # Gets the HTML of recipe's website 
    urllib_request = urllib.request.Request(recipe.recipe_url, data=None, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    })
    url_file = urllib.request.urlopen(urllib_request)
    website_html = url_file.read().decode('UTF-8')

    # Creates a random file name
    file_name = secrets.token_hex()

    # Saves the HTML to a file
    html_file = open("recipe_files/{}.html".format(file_name), "w")
    html_file.write(website_html)
    html_file.close()

    # Uploads the recipe to OpenAI
    file_upload_response = await upload_file(file_name)
    file_upload_id = vars(file_upload_response)["id"]

    # Creates the thread for the assistant
    message_thread = openai_client.beta.threads.create(messages=[
        {
            "role": "user",
            "content": "Please extract the recipe data from the file with this ID: {}".format(file_upload_id),
            "attachments": [{"file_id": file_upload_id, "tools": [{"type": "file_search"}, {"type": "code_interpreter"}]}]
        }
        ])

    # Gets the thread id from the response
    message_thread_id = vars(message_thread)["id"]

    # Runs the thread to extract the recipe data
    run = openai_client.beta.threads.runs.create(
      thread_id=message_thread_id,
      assistant_id=os.getenv("OpenAI_Assistant_ID")
    )

   # Checks if the run is complete every x seconds 
    while (run.completed_at is None) and (run.failed_at is None):
        sleep(1.5)
        run = openai_client.beta.threads.runs.retrieve(
          thread_id=message_thread_id,
          run_id=run.id
        )
    
    if run.failed_at is not None:
        print(run)
        raise HTTPException(status_code=500, detail="Couldn't extract the recipe's information")

    # Gets the last message from the thread (which is the AI's response)
    ai_response = openai_client.beta.threads.messages.list(message_thread_id, run_id=run.id).data[0].content[0].text.value

    # Extracts just the JSON from the response
    if "```json" in ai_response:
        re_pattern = r"```.+```"
        extracted_recipe_json_string = re.search(re_pattern, ai_response, re.DOTALL).group().replace("```", "").replace("json", "")
        extracted_recipe = json.loads(extracted_recipe_json_string)

    else:
        extracted_recipe = json.loads(ai_response)

    # Deletes the uploaded file
    openai_client.files.delete(file_upload_id)
    os.remove("recipe_files/{}.html".format(file_name))

    # Saves the data to the Recipes table
    recipe_table_data = extracted_recipe["Extra_Information"]

    recipe_table_data["Recipe_URL"] = recipe.recipe_url 
    recipe_table_data["Recipe_Name"] = extracted_recipe["Recipe_Name"]

    # Saves the data to the Ingredients table
    ingredients_table_data = extracted_recipe["Ingredients"]

    # Saves the data to the Steps table
    steps_table_data = extracted_recipe["Steps"]

    # Gets the user id
    user_id = get_user_id(request)

    # Adds the User ID to the recipe_table_data
    recipe_table_data["User_ID"] = user_id 

    # Inserts the data to the Recipe table
    insert_query = insert(recipes_table).values(recipe_table_data)
    result = connection.execute(insert_query)

    # Gets the recipe id
    recipe_id = result.inserted_primary_key[0]
    
    # Adds the recipe id to each of the steps
    for step in steps_table_data:
        step["Recipe_ID"] = recipe_id
        
    # Adds the recipe id to each of the ingredients
    for ingredient in ingredients_table_data:
        ingredient["Recipe_ID"] = recipe_id

    # Saves the data to the database
    connection.execute(insert(steps_table), steps_table_data)
    connection.execute(insert(ingredients_table), ingredients_table_data)

    connection.commit()

    # Removes the User_ID before sending the recipe data to the user
    recipe_table_data.pop("User_ID", None)

    return extracted_recipe
