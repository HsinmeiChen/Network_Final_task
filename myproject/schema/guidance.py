from typing import List, Optional
from pydantic import BaseModel, Field

# 定義 API Input 類別
class GuidanceRequest(BaseModel):
    questionDescription: str = Field(..., example="Describe the key elements in the image provided.")
    studentResponse: str = Field(..., example="The image shows a forest with several animals.")
    guidanceDirections: List[str] = Field(
        ...,
        example=[
            "Focus on identifying the specific animals in the image.",
            "Describe the types of trees present in the forest."
        ]
    )

# 定義 API Output 的子結構
class GuidanceStatus(BaseModel):
    guidanceDirection: str = Field(..., example="Focus on identifying the specific animals in the image.")
    isFulfilled: bool = Field(..., example=True)
    commentary: Optional[str] = Field(
        None,
        example="Ah, splendid! You’ve unveiled the creatures roaming the forest. But beware, the trees remain silent in your story—what secrets do they hold?"
    )

# 定義 API Output 類別
class GuidanceResponse(BaseModel):
    feedback: str = Field(
        ...,
        example="Your description has set the stage beautifully, painting the forest scene vividly! But alas, a curious observer might yearn for tales of what lies beneath the canopy and the creatures that frolic within. Could you bring these details to light in your narrative?"
    )
    guidanceStatus: List[GuidanceStatus] = Field(
        ...,
        example=[
            {
                "guidanceDirection": "Focus on identifying the specific animals in the image.",
                "isFulfilled": True,
                "commentary": "Ah, splendid! You’ve unveiled the creatures roaming the forest. But beware, the trees remain silent in your story—what secrets do they hold?"
            },
            {
                "guidanceDirection": "Describe the types of trees present in the forest.",
                "isFulfilled": False,
                "commentary": "The trees stand tall, waiting patiently for their moment to shine in your tale. Perhaps you could grant them a voice in your narrative?"
            }
        ]
    )

# 定義 API 錯誤回應類別
class ErrorResponse(BaseModel):
    error: str = Field(..., example="Invalid input format. Ensure all required fields are provided and correctly formatted.")

# 測試用例
if __name__ == "__main__":
    # 構造輸入測試
    input_data = GuidanceRequest(
        questionDescription="Describe the key elements in the image provided.",
        studentResponse="The image shows a forest with several animals.",
        guidanceDirections=[
            "Focus on identifying the specific animals in the image.",
            "Describe the types of trees present in the forest."
        ]
    )
    print("Input JSON:")
    print(input_data.model_dump_json(indent=4))

    # 構造輸出測試
    output_data = GuidanceResponse(
        feedback="Your description has set the stage beautifully, painting the forest scene vividly! But alas, a curious observer might yearn for tales of what lies beneath the canopy and the creatures that frolic within. Could you bring these details to light in your narrative?",
        guidanceStatus=[
            GuidanceStatus(
                guidanceDirection="Focus on identifying the specific animals in the image.",
                isFulfilled=True,
                commentary="Ah, splendid! You’ve unveiled the creatures roaming the forest. But beware, the trees remain silent in your story—what secrets do they hold?"
            ),
            GuidanceStatus(
                guidanceDirection="Describe the types of trees present in the forest.",
                isFulfilled=False,
                commentary="The trees stand tall, waiting patiently for their moment to shine in your tale. Perhaps you could grant them a voice in your narrative?"
            )
        ]
    )
    print("\nOutput JSON:")
    print(output_data.model_dump_json(indent=4))

    # 測試錯誤回應
    error_data = ErrorResponse(error="Invalid input format. Ensure all required fields are provided and correctly formatted.")
    print("\nError JSON:")
    print(error_data.model_dump_json(indent=4))
