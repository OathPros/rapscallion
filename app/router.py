import re
from typing import Any

from rapidfuzz import fuzz

from app.catalogue import load_service_catalogue

INCIDENT_KEYWORDS = {
    "outage",
    "down",
    "breach",
    "hacked",
    "urgent",
    "cannot login",
    "can't login",
    "locked out",
    "compromised",
    "phishing",
}

SERVICE_REQUEST_KEYWORDS = {
    "request",
    "need access",
    "grant access",
    "install",
    "setup",
    "set up",
    "reset",
    "update",
    "create",
}

GUIDED_SUPPORT_KEYWORDS = {
    "how do i",
    "how to",
    "steps",
    "guide",
    "where can i",
    "help me",
}


class ServiceRouter:
    def __init__(self) -> None:
        self.catalogue = load_service_catalogue()

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    def _best_catalogue_match(self, message: str) -> dict[str, Any] | None:
        best = None
        best_score = 0.0
        for service in self.catalogue:
            candidates = [service["name"], *service.get("keywords", []), *service.get("aliases", [])]
            for candidate in candidates:
                score = fuzz.token_set_ratio(message, candidate) / 100.0
                if score > best_score:
                    best_score = score
                    best = service

        if best is None:
            return None

        return {"service": best, "score": round(best_score, 3)}

    def classify(self, message: str) -> dict[str, Any]:
        normalized = self._normalize(message)
        match_info = self._best_catalogue_match(normalized)

        matched_service = match_info["service"] if match_info else None
        confidence = match_info["score"] if match_info else 0.0

        incident_hit = any(k in normalized for k in INCIDENT_KEYWORDS)
        request_hit = any(k in normalized for k in SERVICE_REQUEST_KEYWORDS)
        guided_hit = any(k in normalized for k in GUIDED_SUPPORT_KEYWORDS)

        route = "knowledge_answer"
        state_change_required = False
        knowledge_can_solve = True
        missing_fields: list[str] = []
        next_action = "Answer directly using knowledge base content."

        # Priority: incident first, then service request
        if incident_hit:
            route = "incident_escalation"
            state_change_required = True
            knowledge_can_solve = False
            next_action = "Escalate to IT incident response queue and collect urgency/contact details."
            if "contact" not in normalized and "phone" not in normalized:
                missing_fields.append("contact_method")
        elif request_hit or (matched_service and confidence >= 0.55 and matched_service.get("requires_state_change", False)):
            route = "service_request"
            state_change_required = True
            knowledge_can_solve = False
            next_action = "Create or route a service ticket and gather required request fields."
            required_fields = matched_service.get("required_fields", []) if matched_service else []
            for field in required_fields:
                if field.replace("_", " ") not in normalized:
                    missing_fields.append(field)
        elif guided_hit or (matched_service and confidence >= 0.5):
            route = "guided_support"
            state_change_required = False
            knowledge_can_solve = True
            next_action = "Provide guided troubleshooting steps for the user."
        else:
            route = "knowledge_answer"
            state_change_required = False
            knowledge_can_solve = True
            next_action = "Answer directly or ask one clarifying question."

        return {
            "route": route,
            "confidence": round(confidence, 3),
            "matched_service_id": matched_service["id"] if matched_service else None,
            "matched_name": matched_service["name"] if matched_service else None,
            "state_change_required": state_change_required,
            "knowledge_can_solve": knowledge_can_solve,
            "missing_fields": sorted(set(missing_fields)),
            "next_action": next_action,
        }
