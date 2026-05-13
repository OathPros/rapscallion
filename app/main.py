from fastapi import FastAPI

from app.router import ServiceRouter
from app.schemas import ClassifyRequest, ClassifyResponse

app = FastAPI(title="York Service Router", version="0.1.0")
router = ServiceRouter()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/classify", response_model=ClassifyResponse)
def classify(payload: ClassifyRequest) -> ClassifyResponse:
    result = router.classify(payload.message)
    return ClassifyResponse(**result)
