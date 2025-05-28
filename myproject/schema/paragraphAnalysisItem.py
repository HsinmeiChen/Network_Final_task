from pydantic import BaseModel
from typing import List, Optional

class ParagraphAnalysisItem(BaseModel):
    paragraph: str  # A single paragraph from the user's response
    relevanceScore: float  # The relevance score of the paragraph to the base statement
    paragraphResponse: str  # A response message mainly based on the input baseStatement and addressing the content of the paragraph

class AnalyzeResponseRequest(BaseModel):
    baseStatement: str  # The base statement to evaluate the response against
    userResponse: str  # The user's full response to be analyzed

class AnalyzeResponseResponse(BaseModel):
    paragraphAnalysis: List[ParagraphAnalysisItem]  # Analysis of each paragraph in the user's response
