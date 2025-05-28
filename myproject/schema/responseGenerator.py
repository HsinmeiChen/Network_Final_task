from pydantic import BaseModel
from typing import Optional

class GenerateResponseRequest(BaseModel):
    baseStatement: str  # 根據的指定敘述
    userStatement: str  # 使用者的敘述

class GenerateResponseResponse(BaseModel):
    baseStatement: str  # The base statement provided
    userStatement: str  # The original user's input statement
    responseStatement: str  # The response generated
    responseRelevanceScore: float  # Degree to which the response matches the base statement
