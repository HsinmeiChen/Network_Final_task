from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ValidationError


# Enum for response types as defined in the Swagger spec
class ResponseTypeEnum(str, Enum):
    ANALYTICAL = "Analytical Response"
    APPRECIATIVE = "Appreciative Response"
    APOLOGETIC = "Apologetic Response"
    AVOIDANCE = "Avoidance Response"
    AVOIDING_EMOTIONS = "Avoiding Emotions Response"
    CALM = "Calm Response"
    CHALLENGING = "Challenging Response"
    COMPARATIVE = "Comparative Response"
    COMPETITIVENESS = "Competitiveness Response"
    CONFIRMATION = "Confirmation Response"
    CONSTRUCTIVE_CRITICISM = "Constructive Criticism Response"
    CONTEXTUAL = "Contextual Response"
    COUNTERQUESTION = "Counterquestion Response"
    CRITICISM = "Criticism Response"
    CYNICAL = "Cynical Response"
    DEFENSIVE = "Defensive Response"
    DELEGATION = "Delegation Response"
    DENIAL_OF_RESPONSIBILITY = "Denial of Responsibility Response"
    DERISIVE = "Derisive Response"
    DESCRIPTIVE = "Descriptive Response"
    DISTRESS = "Distress Response"
    EMOTIONAL = "Emotional Response"
    EMPHASIZED = "Emphasized Response"
    ENCOURAGEMENT = "Encouragement Response"
    EXACT = "Exact Response"
    EXCITED = "Excited Response"
    EXPLORATORY = "Exploratory Response"
    EXPECTATION = "Expectation Response"
    FOCUS_ORIENTED = "Focus-Oriented Response"
    FUTURE_ORIENTED = "Future-Oriented Response"
    HUMOROUS = "Humorous Response"
    INDIFFERENCE = "Indifference Response"
    INDUCTIVE = "Inductive Response"
    INSIGHTFUL = "Insightful Response"
    LOGICAL_THINKING = "Logical Thinking Response"
    MEANINGLESS = "Meaningless Response"
    MODESTY = "Modesty Response"
    MORAL_JUDGMENT = "Moral Judgment Response"
    MORAL_PERSUASION = "Moral Persuasion Response"
    NEGATIVE = "Negative Response"
    NEUTRAL = "Neutral Response"
    NO_RESPONSE = "No Response"
    POSITIVE = "Positive Response"
    REBUTTAL = "Rebuttal Response"
    REFLECTION = "Reflection Response"
    RELEASE_TENSION = "Release Tension Response"
    RELUCTANT = "Reluctant Response"
    REITERATIVE = "Reiterative Response"
    RESPONSIBILITY_SHIFTING = "Responsibility-Shifting Response"
    SACRIFICE = "Sacrifice Response"
    SARCASTIC = "Sarcastic Response"
    SELF_PRAISE = "Self-Praise Response"
    SELF_REFLECTIVE = "Self-Reflective Response"
    SILENT_PROTEST = "Silent Protest Response"
    SPECULATIVE = "Speculative Response"
    SUGGESTION = "Suggestion Response"
    SUPPORTIVE = "Supportive Response"
    SYMPATHETIC = "Sympathetic Response"
    TIME_DELAYING = "Time Delaying Response"
    TOPIC_SHIFTING = "Topic Shifting Response"
    VAGUE = "Vague Response"


# Input schema
class ClassifyResponseInputQA(BaseModel):
    question: str = Field(..., description="The question that was asked to the user.")
    userResponse: str = Field(..., description="The response provided by the user.")

# Input schema
class ClassifyResponseInputNarrative(BaseModel):
    narrative: List[str] = Field(
        ..., 
        description="The narrative provided to the user as a list of sentences"
    )
    userResponse: str = Field(..., description="The response provided by the user.")

# Output schema for a successful response
class ClassifyResponseOutput(BaseModel):
    responseType: ResponseTypeEnum = Field(..., description="The classified type of the user's response.")
    reply: str = Field(..., description="The appropriate reply based on the user's response type.")


# Output schema for an error response
class ErrorResponse(BaseModel):
    error: str = Field(..., description="錯誤訊息，解釋發生了什麼問題。")


# Example function to classify the response
class UserResponseClassifier:
    def classify_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Parse and validate the input data
            input_data = ClassifyResponseInputQA(**data)
            
            # Example classification logic (stubbed)
            # Replace this with the actual classification logic.
            response_type = ResponseTypeEnum.CRITICISM
            reply = "感謝您的反饋，我們會考慮改進鍵盤的按鍵手感。"
            
            # Return the classified response
            output_data = ClassifyResponseOutput(
                responseType=response_type,
                reply=reply
            )
            return output_data.model_dump()

        except ValidationError as e:
            # Return an error response if input validation fails
            error_response = ErrorResponse(error=str(e))
            return error_response.model_dump()
