from pydantic import BaseModel, Field


class ClassifyRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ClassifyResponse(BaseModel):
    route: str
    confidence: float
    matched_service_id: str | None
    matched_name: str | None
    state_change_required: bool
    knowledge_can_solve: bool
    missing_fields: list[str]
    next_action: str
