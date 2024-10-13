import os

from openai import OpenAI
from dotenv import load_dotenv

# Loads the enviroment variables
load_dotenv()

openai_client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OpenAI_API_KEY"),
)
