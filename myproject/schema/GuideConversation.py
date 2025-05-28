from pydantic import BaseModel, Field

class GuideConversationRequest(BaseModel):
    guidanceContent: str = Field(..., description="🔥 The powerful guiding content to steer the conversation like a master orator! 🎤")
    userSituation: str = Field(..., description="💡 The grand tale of the user's predicament that needs the wisdom of this legendary API! 📖")

class GuideConversationResponse(BaseModel):
    responseContent: str = Field(..., description="🎇 The majestic, awe-inspiring, and impeccably crafted response tailored just for you! 🎇")
