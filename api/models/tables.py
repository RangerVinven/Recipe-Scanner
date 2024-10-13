from sqlalchemy import Column, Integer, String, Table, MetaData, ForeignKeyConstraint, Text
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
Base = declarative_base()

# The users table
users_table = Table(
        "Users",
        metadata,
        Column("User_ID", Integer, primary_key=True, autoincrement=True),
        Column("First_Name", String(20), nullable=False),
        Column("Email", String(50), nullable=False, unique=True),
        Column("Password", String(256), nullable=False),
        Column("Preferred_Units", String(10), nullable=False, default='metric')
    )

# The sessions token table
session_tokens_table = Table(
    "Session_Tokens",
    metadata,
    Column("User_ID", Integer, nullable=False),
    Column("Session_Token", String(256), nullable=False, unique=True),
    ForeignKeyConstraint(['User_ID'], ['Users.User_ID'], 
                         name='Session_Tokens_Users_FK',
                         ondelete='CASCADE', 
                         onupdate='CASCADE')
)

# The recipes token table
recipes_table = Table(
    "Recipes",
    metadata,
    Column("Recipe_ID", Integer, primary_key=True, autoincrement=True),
    Column("Recipe_Name", String(100), nullable=False),
    Column("Servings", Integer, nullable=True),
    Column("Cook_Time_In_Minutes", Integer, nullable=True),
    Column("Calories", Integer, nullable=True),
    Column("Carbs", Integer, nullable=True),
    Column("Protein", Integer, nullable=True),
    Column("Fats", Integer, nullable=True),
    Column("Sugars", Integer, nullable=True),
    Column("User_ID", Integer, nullable=False),
    Column("Recipe_URL", String(256), nullable=True),
    ForeignKeyConstraint(['User_ID'], ['Users.User_ID'], 
                         name='Recipes_Users_FK', 
                         ondelete='CASCADE', 
                         onupdate='CASCADE')
)

# The ingredients token table
ingredients_table = Table(
    "Ingredients",
    metadata,
    Column("Ingredient_ID", Integer, primary_key=True, autoincrement=True),
    Column("Ingredient_Name", String(100), nullable=False),
    Column("Ingredient_Amount", String(10), nullable=False),
    Column("Ingredient_Unit", String(10), nullable=False),
    Column("Recipe_ID", Integer, nullable=False),
    ForeignKeyConstraint(['Recipe_ID'], ['Recipes.Recipe_ID'], 
                         name='Ingredients_Recipes_FK', 
                         ondelete='CASCADE', 
                         onupdate='CASCADE')
)

# The steps token table
steps_table = Table(
    "Steps",
    metadata,
    Column("Step_ID", Integer, primary_key=True, autoincrement=True),
    Column("Step_Number", Integer, nullable=False),
    Column("Step", Text, nullable=False),
    Column("Recipe_ID", Integer, nullable=False),
    ForeignKeyConstraint(['Recipe_ID'], ['Recipes.Recipe_ID'], 
                         name='Steps_Recipes_FK', 
                         ondelete='CASCADE', 
                         onupdate='CASCADE')
)
