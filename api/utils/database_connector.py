# I followed this tutorial to learn about sqlalchemy
# I've modified and applied the code for my project, but some of it may look similar
# https://www.youtube.com/watch?v=aAy-B6KPld8

import os
import sqlalchemy as sa

from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, Table, MetaData 

# Loads the enviroment variables
load_dotenv()

# Database enviroment variables
username = os.getenv("Database_Username")
password = os.getenv("Database_Password")
host = os.getenv("Database_Host")
database_name = os.getenv("Database_Name")

# Connects to the database
engine = sa.create_engine("mysql+mysqlconnector://{}:{}@{}/{}".format(username, password, host, database_name));
connection = engine.connect()

