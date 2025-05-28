from pydantic import BaseModel, Field

class AnswerFeedbackRequest(BaseModel):
    userMessage: str = Field(..., description="使用者訊息")
    answer: bool = Field(..., description="使用者作答正確與否")
    errorCount: int = Field(..., description="錯誤次數")

class AnswerFeedbackResponse(BaseModel):
    replyMessage: str = Field(..., description="給予使用者浮誇的回覆訊息")