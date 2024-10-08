import re
from fastapi import HTTPException

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from utils.database_connector import connection

# Tries to save the user into the database 
async def insert_data(table_model, data):

    try:
        # Creates and executes the query
        insert_query = insert(table_model).values(vars(data))
        result = connection.execute(insert_query)

        # Saves the change to the database
        connection.commit()

        return result

    # Throws an error if an entry already exists
    except IntegrityError as error:
        duplicate_value = duplicate_error_extractor(str(error))
        raise HTTPException(status_code=409, detail="{} already exists".format(duplicate_value))

# Extracts what parameter is a duplicate when recieving an IntegrityError 
def duplicate_error_extractor(error_message):
    # Finds the duplicate value
    pattern = r"Duplicate entry '(.+?)'"
    match = re.search(pattern, error_message)

    if match:
        duplicate_value = match.group(0)
        return duplicate_value

    else: 
        return "Couldn't find the duplicate value"
