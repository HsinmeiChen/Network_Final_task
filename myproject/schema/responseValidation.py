from pydantic import BaseModel, Field
from typing import Optional, List

# 定義 Request Body 的結構
class ValidateResponseRequest(BaseModel):
    userResponse: str = Field(
        ..., 
        description="The response provided by the user, which may include the solution process."
    )
    question: str = Field(
        ..., 
        description="The description of the question."
    )
    correctAnswer: List[str] = Field(
        ..., 
        description="An array of correct answers to the question."
    )
    requireAllCorrect: bool = Field(
        ..., 
        description="If true, the userResponse must match all answers in the correctAnswer array. If false, matching any one answer is sufficient."
    )

# 定義成功 Response 的結構
class AnswerFeedback(BaseModel):
    answer: str = Field(
        ..., 
        description="A specific correct answer."
    )
    isCorrect: bool = Field(
        ..., 
        description="Indicates if the user's response matches this specific answer."
    )
    feedback: str = Field(
        ..., 
        description="Feedback for the user regarding this specific answer."
    )
    userAnswerSnippet: str = Field(
        "", 
        description="The segment of the user's response related to this specific answer. Empty if isCorrect is false."
    )
    translatedResponse: Optional[str] = Field(
        None, 
        description="The user's response translated into the correct answer's language (if language matching is enabled)."
    )
    semanticSimilarity: Optional[float] = Field(
        None, 
        description="Semantic similarity score (range 0 to 1). A score above 0.8 is typically considered correct."
    )

class ValidateResponseResponse(BaseModel):
    answers: List[AnswerFeedback] = Field(
        ..., 
        description="A list of feedback for each correct answer."
    )

# 定義 400 Bad Request Response 的結構
class ErrorResponse(BaseModel):
    error: str = Field(
        ..., 
        description="Error message describing why the input was invalid."
    )
