# york-service-router

A FastAPI prototype for routing York University chatbot support messages into one of four routes:

- `knowledge_answer`
- `guided_support`
- `service_request`
- `incident_escalation`

## Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn app.main:app --reload
```

API base URL: `http://127.0.0.1:8000`

## Swagger docs

Open:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Classify endpoint

`POST /api/classify`

Request body:

```json
{
  "message": "Please reset my Duo, I switched phones"
}
```

Response shape:

```json
{
  "route": "service_request",
  "confidence": 0.86,
  "matched_service_id": "svc_duo_reset",
  "matched_name": "Duo device reset",
  "state_change_required": true,
  "knowledge_can_solve": false,
  "missing_fields": ["device_type", "student_or_staff_id"],
  "next_action": "Create or route a service ticket and gather required request fields."
}
```

## Run tests

```bash
pytest -q
```

## Routing logic summary

The classifier uses deterministic routing:

1. Keyword rules (`incident` and `service request` first).
2. RapidFuzz catalogue matching against service names, aliases, and keywords.
3. Priority rules: `incident_escalation` > `service_request` > `guided_support` > `knowledge_answer`.
