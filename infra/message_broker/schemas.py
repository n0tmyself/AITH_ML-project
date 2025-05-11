from pydantic import BaseModel

class TextGenerationTask(BaseModel):
    user_id: int
    prompt: str
    task_id: str

class BillingEvent(BaseModel):
    user_id: int
    task_id: str
    credits_used: int
    success: bool