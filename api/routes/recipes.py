import os
import secrets
import requests
import urllib.request, urllib.error, urllib.parse

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Response, Request

from models.recipes import GenerateRecipe

load_dotenv()

recipes_router = APIRouter()

# Uploads a file to OpenAI
async def upload_file(file_name):
    url = "https://api.openai.com/v1/files"
    headers = {
        "Authorization": "Bearer {}".format(os.environ["OpenAI_API_KEY"])
    }

    file = {"purpose": "assistants", "file": (file_name, open("recipe_files/{}.html".format(file_name), "rb"))}

    upload_response = requests.post(url, headers=headers, files=file)
    print(upload_response)

@recipes_router.post("/extract_recipe")
async def generate_recipe(recipe: GenerateRecipe):
    # Downloads the HTML of recipe's website 
    url_file = urllib.request.urlopen(recipe.recipe_url)
    website_html = url_file.read().decode('UTF-8')

    # Creates a random file name
    file_name = secrets.token_hex()

    # Saves the HTML to a file
    html_file = open("recipe_files/{}.html".format(file_name), "w")
    html_file.write(website_html)
    html_file.close()

    # Uploads the recipe to OpenAI
    await upload_file(file_name)

    # Asks OpenAI to extract the relivant information from the recipe
