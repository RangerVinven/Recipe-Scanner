from pydantic import BaseModel
from typing import List

class Steps(BaseModel):
    Step_ID: int
    Step_Number: int
    Step: str
    Recipe_ID: int

class Step(BaseModel):
    Step_Number: int
    Step: str

class StepWithID(Step):
    Step_ID: int

class CreateSteps(BaseModel):
    Steps: List[Step] = []

class UpdateSteps(BaseModel):
    Steps: List[StepWithID] = []
