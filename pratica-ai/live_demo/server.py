"""FastAPI backend for the PraticaAI UI.

The browser transport lives here. Claim workflow execution lives in agent.py,
which defines and runs the ADK graph.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import json
import logging
import os
import re
import sys
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, date
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.websockets import WebSocketState

APP_DIR = Path(__file__).resolve().parents[1]
DEMO_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


def _load_dotenv() -> None:
    env_path = APP_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _cors_origins() -> list[str]:
    raw = os.getenv("FNOL_CORS_ORIGINS", "")
    if raw.strip():
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return ["http://127.0.0.1:4177", "http://localhost:4177"]


_load_dotenv()

from agent import (  # noqa: E402
    MODEL,
    blank_claim,
    build_initial_workflow_state,
    run_claim_workflow,
)
from llm_provider import LLMProvider  # noqa: E402  # === FIX 2 ===
from schemas import ClaimClassification, ClaimNarrative  # noqa: E402
from database import (  # noqa: E402
    init_db,
    get_db,
    create_sinistro,
    get_sinistro_by_session,
    update_sinistro_claim_data,
    add_transcript_turn,
    get_all_sinistri,
)
from auth import router as auth_router, get_current_operator, OperatorOut  # noqa: E402
from gdpr import (  # noqa: E402
    router as gdpr_router,
    verifica_consenso,
    log_accesso_dati_sensibili,
    TESTO_CONSENSO_TRATTAMENTO,
    TESTO_CONSENSO_DATI_SENSIBILI,
    CONSENSO_VERSIONE,
)

# === FIX 2: Voice model from LLM provider abstraction ===
LIVE_MODEL = LLMProvider.get_voice_model()
GENAI_CLIENT = None
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Monitoring infrastructure
# ---------------------------------------------------------------------------

SERVER_START_TIME = time.time()
LOG_BUFFER: deque[dict] = deque(maxlen=500)
ERROR_COUNTER: deque[dict] = deque(maxlen=100)
QUOTA_COUNTER: dict = {"date": None, "count": 0}


# === FIX 5: Gemini quota manager ===
class GeminiQuotaManager:
    """Tracks Gemini API usage to prevent hitting free tier limits.

    Resets daily at midnight UTC.
    """

    def __init__(self, daily_limit: int = 20):
        self.daily_limit = daily_limit
        self.count = 0
        self.date = date.today()

    def _reset_if_new_day(self):
        today = date.today()
        if today != self.date:
            self.count = 0
            self.date = today
            log_event("INFO", f"Quota Gemini azzerata — nuovo giorno: {today}")

    def can_call(self) -> bool:
        self._reset_if_new_day()
        return self.count < self.daily_limit

    def record_call(self):
        self._reset_if_new_day()
        self.count += 1
        remaining = self.daily_limit - self.count
        level = "WARNING" if remaining <= 5 else "INFO"
        log_event(
            level,
            f"Gemini chiamata #{self.count} oggi ({remaining} rimanenti)",
        )

    def get_status(self) -> dict:
        self._reset_if_new_day()
        return {
            "used": self.count,
            "limit": self.daily_limit,
            "remaining": self.daily_limit - self.count,
            "percentage": round(self.count / self.daily_limit * 100),
            "is_exhausted": self.count >= self.daily_limit,
        }


quota_manager = GeminiQuotaManager(
    daily_limit=int(os.getenv("GEMINI_DAILY_LIMIT", "20"))
)
SINISTRI_OGGI: dict = {"date": None, "count": 0}
_monitor_ws_clients: set[WebSocket] = set()


def _quota_today() -> int:
    """Return and lazily reset daily Gemini API call counter."""
    today = date.today().isoformat()
    if QUOTA_COUNTER["date"] != today:
        QUOTA_COUNTER["date"] = today
        QUOTA_COUNTER["count"] = 0
    return QUOTA_COUNTER["count"]


def _increment_quota() -> int:
    _quota_today()  # ensure reset
    QUOTA_COUNTER["count"] += 1
    return QUOTA_COUNTER["count"]


def _sinistri_today() -> int:
    today = date.today().isoformat()
    if SINISTRI_OGGI["date"] != today:
        SINISTRI_OGGI["date"] = today
        SINISTRI_OGGI["count"] = 0
    return SINISTRI_OGGI["count"]


def _increment_sinistri() -> int:
    _sinistri_today()  # ensure reset
    SINISTRI_OGGI["count"] += 1
    return SINISTRI_OGGI["count"]


def _errors_last_hour() -> int:
    cutoff = time.time() - 3600
    return sum(
        1 for e in ERROR_COUNTER
        if datetime.fromisoformat(e["timestamp"]).timestamp() > cutoff
    )


async def broadcast_to_monitors(entry: dict) -> None:
    """Push a log entry to all connected monitor WebSocket clients."""
    dead: list[WebSocket] = []
    payload = json.dumps(entry)
    for ws in list(_monitor_ws_clients):
        try:
            if ws.client_state == WebSocketState.CONNECTED:
                await ws.send_text(payload)
            else:
                dead.append(ws)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _monitor_ws_clients.discard(ws)


def log_event(
    level: str,
    message: str,
    session_id: str | None = None,
    source: str | None = None,
) -> None:
    entry = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
        "session_id": session_id,
        "source": source or "server.py",
    }
    LOG_BUFFER.appendleft(entry)
    if level == "ERROR":
        ERROR_COUNTER.appendleft(entry)
    # Also log to standard logger for file/console output
    log_fn = getattr(logger, level.lower(), logger.info)
    log_fn(message)
    # Broadcast to monitor WS clients (fire-and-forget)
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(broadcast_to_monitors(entry))
    except RuntimeError:
        pass  # no event loop running yet (startup)


class MessageRequest(BaseModel):
    session_id: str
    text: str


class SessionResponse(BaseModel):
    session_id: str
    model: str
    has_api_key: bool
    state: dict[str, Any]


@dataclass
class IntakeSession:
    session_id: str
    transcript: list[dict[str, str]] = field(default_factory=list)
    normalized_claim: dict[str, Any] | None = None
    classification: dict[str, Any] | None = None
    route: str = "needs_docs"
    escalation_required: bool = False
    escalation_reason: str = ""


# Sessions are now persisted in pratica_ai_db.db
# In-memory cache for active WebSocket connections only
active_ws_sessions: dict[str, Any] = {}

# Legacy in-memory dict kept for text-mode /api/sessions and /api/message
# endpoints that still use IntakeSession objects during a single request.
sessions: dict[str, IntakeSession] = {}

app = FastAPI(title="PraticaAI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Startup: initialize database tables
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    await init_db()


# ---------------------------------------------------------------------------
# Include auth router
# ---------------------------------------------------------------------------

app.include_router(auth_router)
app.include_router(gdpr_router)


def _has_api_key() -> bool:
    return bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))


def _client():
    global GENAI_CLIENT
    if not _has_api_key():
        raise HTTPException(
            status_code=503,
            detail=(
                "Missing GOOGLE_API_KEY. Add it to "
                f"{APP_DIR / '.env'} and restart the live intake backend."
            ),
        )
    if os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]
    try:
        from google import genai
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail="Missing google-genai package. Run pip install -r requirements.txt.",
        ) from exc
    if GENAI_CLIENT is None:
        GENAI_CLIENT = genai.Client()
    return GENAI_CLIENT


def _claim_from_session(session: IntakeSession) -> dict[str, Any]:
    return session.normalized_claim or blank_claim()


def _claimant_text(session: IntakeSession) -> str:
    return "\n".join(
        turn["text"] for turn in session.transcript if turn["speaker"] == "Claimant"
    )


def _status(value: Any, urgent: bool = False) -> str:
    text = str(value or "").strip().lower()
    if urgent:
        return "urgent"
    if text in {"", "unknown", "not specified", "unspecified", "n/a", "none", "not provided"}:
        return "missing"
    return "complete"


def _without_negated_safety_mentions(text: str) -> str:
    cleaned = str(text or "")
    for pattern in [
        r"\b(?:no|not|none|without|denies|denied)\s+(?:one\s+)?(?:was\s+)?(?:injur\w*|hurt|pain|medical attention|ambulance|hospital|unsafe|hazard\w*|danger)\b",
        r"\b(?:injur\w*|hurt|pain|medical attention|ambulance|hospital|unsafe|hazard\w*|danger)\s+(?:was|were|is|are)?\s*(?:reported\s+)?(?:no|none|not reported|denied)\b",
    ]:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
    return cleaned


def _has_negated_safety_mention(text: str) -> bool:
    return _without_negated_safety_mentions(text) != str(text or "")


def _positive_safety_items(items: list[str]) -> list[str]:
    patterns = [
        r"\binjur",
        r"\bhurt\b",
        r"\bneck pain\b",
        r"\bhospital\b",
        r"\burgent care\b",
        r"\bambulance\b",
        r"\bunsafe\b",
        r"\bhazard",
        r"\bdanger\b",
    ]
    return [
        item
        for item in items
        if any(
            re.search(pattern, _without_negated_safety_mentions(item), flags=re.IGNORECASE)
            for pattern in patterns
        )
    ]


def _join(items: list[str], fallback: str) -> str:
    return ", ".join(items) if items else fallback


def _field(label: str, value: Any, source: str = "Gemini extraction", urgent: bool = False) -> dict[str, str]:
    status = _status(value, urgent=urgent)
    display = value if status != "missing" else f"Missing: {label.lower()}"
    return {
        "label": label,
        "value": str(display),
        "status": status,
        "source": "-" if status == "missing" else source,
    }


def _items_containing(items: list[str], needles: list[str], fallback: str = "Unknown") -> str:
    matches = [
        item
        for item in items
        if any(needle in item.lower() for needle in needles)
    ]
    return _join(matches, fallback)


def _events(
    session: IntakeSession,
    validation: dict[str, Any],
    coverage: dict[str, Any],
    fraud_gate: dict[str, Any],
) -> list[dict[str, str]]:
    events: list[dict[str, str]] = [
        {
            "tone": "success",
            "title": "Gemini extraction complete",
            "detail": f"Updated structured claim facts using {MODEL}.",
            "rule": "LLM-001",
        }
    ]
    if validation.get("missing_fields"):
        events.append(
            {
                "tone": "warning",
                "title": "Missing intake facts",
                "detail": ", ".join(validation["missing_fields"]),
                "rule": "INTAKE-001",
            }
        )
    for finding in coverage.get("findings", []):
        tone = "danger" if finding["required_action"] == "emergency_escalation" else "warning"
        if finding["required_action"] == "adjuster_review":
            tone = "success"
        events.append(
            {
                "tone": tone,
                "title": finding["message"],
                "detail": f"Required action: {finding['required_action']}.",
                "rule": finding["rule_id"],
            }
        )
    for signal in fraud_gate.get("signals", []):
        tone = "danger" if signal.get("route_to_emergency") else "warning"
        events.append(
            {
                "tone": tone,
                "title": signal["message"],
                "detail": "Deterministic fraud/safety gate signal.",
                "rule": signal["signal_id"],
            }
        )
    route = fraud_gate.get("final_routing_decision", coverage.get("routing_decision"))
    if route != session.route:
        events.append(
            {
                "tone": "danger" if route == "emergency_escalation" else "success",
                "title": "Routing changed",
                "detail": f"{session.route} -> {route}.",
                "rule": "ROUTE-001",
            }
        )
    return events


def _ui_state(
    session: IntakeSession,
    validation: dict[str, Any],
    coverage: dict[str, Any],
    checklist: dict[str, Any],
    fraud_gate: dict[str, Any],
    packet: dict[str, Any],
    events: list[dict[str, str]],
) -> dict[str, Any]:
    claim = ClaimNarrative.model_validate(_claim_from_session(session))
    classification = ClaimClassification.model_validate(session.classification)
    route = fraud_gate["final_routing_decision"]
    completed = 0

    def counted(field: dict[str, str]) -> dict[str, str]:
        nonlocal completed
        if field["status"] in {"complete", "urgent"}:
            completed += 1
        return field

    positive_safety_items = _positive_safety_items(claim.injuries_or_safety_concerns)
    safety_text = " ".join(
        [
            claim.loss_description,
            claim.raw_narrative_summary,
            _claimant_text(session),
            *claim.injuries_or_safety_concerns,
        ]
    )
    injury_text = _join(claim.injuries_or_safety_concerns, "Unknown")
    if not positive_safety_items and _has_negated_safety_mention(safety_text):
        injury_text = "No injuries reported"
    evidence_text = _join(claim.evidence_available, "Not captured yet")
    required_doc_names = [item["item"] for item in checklist.get("items", [])]

    fields = {
        "claimant": counted(_field("Claimant name", claim.policyholder_name)),
        "policy": counted(_field("Policy number", claim.policy_number)),
        "contact": counted(_field("Contact method", claim.contact_method)),
        "type": counted(_field("Claim type", classification.claim_type.replace("_", " "))),
        "date": counted(_field("Date of loss", claim.date_of_loss)),
        "time": counted(_field("Reported date", claim.reported_date)),
        "location": counted(_field("Location", claim.loss_location)),
        "description": counted(_field("Loss description", claim.loss_description)),
        "injuries": counted(
            _field(
                "Injuries",
                injury_text,
                source="Gemini extraction + safety gate",
                urgent=bool(positive_safety_items),
            )
        ),
        "hazards": counted(
            _field(
                "Hazards present",
                _items_containing(
                    claim.injuries_or_safety_concerns,
                    ["hazard", "unsafe"],
                ),
            )
        ),
        "medical": counted(
            _field(
                "Medical attention",
                _items_containing(
                    claim.injuries_or_safety_concerns,
                    ["medical", "care", "hospital"],
                ),
            )
        ),
        "police": counted(_field("Report number", _find_report(claim))),
        "photos": counted(_field("Evidence available", evidence_text)),
        "tow": counted(_field("Tow info", _find_text(claim, ["tow", "storage"]))),
        "otherDriver": counted(_field("Other driver info", _find_text(claim, ["other driver", "driver", "plate", "witness"]))),
    }

    progress = max(12, round(completed / len(fields) * 100))
    return {
        "route": route,
        "progress": progress,
        "fields": fields,
        "transcript": session.transcript,
        "events": events,
        "handoff": {
            "Summary": packet["adjuster_handoff_summary"],
            "Priority": f"{classification.severity.title()} - {classification.severity_rationale}",
            "Required actions": _join(required_doc_names, "No additional documents identified by current rules."),
            "Attachments": evidence_text,
            "Next best action": packet["claimant_next_message"],
        },
        "packet_markdown": packet["markdown"],
        "model": MODEL,
    }


def _find_text(claim: ClaimNarrative, needles: list[str]) -> str:
    text = " | ".join(
        [claim.loss_description, *claim.evidence_available, *claim.documents_mentioned, *claim.parties_involved]
    )
    lower = text.lower()
    if any(needle in lower for needle in needles):
        return text
    return "not specified"


def _find_report(claim: ClaimNarrative) -> str:
    text = " | ".join([*claim.evidence_available, *claim.documents_mentioned, claim.loss_description])
    lower = text.lower()
    if any(term in lower for term in ["police", "report", "case number", "incident"]):
        return text
    return "not specified"


def _state_from_workflow(session: IntakeSession, workflow: dict[str, Any]) -> dict[str, Any]:
    validation = workflow["field_validation"]
    coverage = workflow["coverage_evidence_decision"]
    checklist = workflow["document_checklist"]
    fraud_gate = workflow["fraud_safety_gate"]
    packet = workflow["claim_intake_packet"]
    session.normalized_claim = workflow["normalized_claim"]
    session.classification = workflow["claim_classification"]
    events = _events(session, validation, coverage, fraud_gate)
    session.route = fraud_gate["final_routing_decision"]
    return _ui_state(session, validation, coverage, checklist, fraud_gate, packet, events)


async def _process_with_adk_graph(
    session: IntakeSession,
    *,
    add_claimant_facing_reply: bool,
) -> dict[str, Any]:
    # === FIX 5: Quota check before every Gemini API call ===
    if not quota_manager.can_call():
        raise HTTPException(
            503,
            detail="Quota Gemini esaurita per oggi. "
                   "Riprova domani o attiva il piano a pagamento.",
        )
    quota_manager.record_call()

    count = _increment_quota()
    log_event("INFO", f"Gemini chiamata #{count} oggi", session_id=session.session_id, source="server.py:_process_with_adk_graph")
    if count >= 18:
        log_event("WARNING", f"Quota Gemini: {count}/20 usate", session_id=session.session_id, source="server.py:_process_with_adk_graph")
    try:
        workflow = await run_claim_workflow(
            _claimant_text(session),
            session_id=session.session_id,
        )
    except Exception as exc:
        err_str = str(exc)
        if "429" in err_str:
            log_event("WARNING", f"Quota Gemini: {count}/20 usate — 429 ricevuto", session_id=session.session_id, source="server.py:_process_with_adk_graph")
        elif "503" in err_str:
            log_event("WARNING", "Gemini non disponibile, retry...", session_id=session.session_id, source="server.py:_process_with_adk_graph")
        else:
            log_event("ERROR", f"Errore Gemini API: {err_str}", session_id=session.session_id, source="server.py:_process_with_adk_graph")
        raise
    if add_claimant_facing_reply:
        packet = workflow["claim_intake_packet"]
        session.transcript.append({"speaker": "Agent", "text": packet["claimant_next_message"]})
    # Track completed claims
    route = workflow.get("fraud_safety_gate", {}).get("final_routing_decision", "")
    if route not in ("needs_docs", ""):
        _increment_sinistri()
        log_event("SUCCESS", f"Sinistro elaborato: {workflow.get('claim_classification', {}).get('claim_type', 'unknown')}", session_id=session.session_id, source="server.py:_process_with_adk_graph")
    return _state_from_workflow(session, workflow)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "version": "1.0", "market": "it"}


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": True, "model": MODEL, "has_api_key": _has_api_key()}


# ---------------------------------------------------------------------------
# Protected dashboard endpoints
# ---------------------------------------------------------------------------


@app.get("/api/sinistri")
async def list_sinistri(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_operator: OperatorOut = Depends(get_current_operator),
) -> list[dict[str, Any]]:
    """Return a paginated list of all claims (requires auth)."""
    async with get_db() as db:
        records = await get_all_sinistri(db, skip=skip, limit=limit)
    return [
        {
            "id": r.id,
            "session_id": r.session_id,
            "stato": r.stato,
            "claim_type": r.claim_type,
            "policyholder_name": r.policyholder_name,
            "codice_fiscale": r.codice_fiscale,
            "provincia": r.provincia,
            "estimated_loss_eur": r.estimated_loss_eur,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        }
        for r in records
    ]


@app.get("/api/sinistri/{session_id}")
async def get_sinistro_detail(
    session_id: str,
    current_operator: OperatorOut = Depends(get_current_operator),
) -> dict[str, Any]:
    """Return a single claim with full data (requires auth)."""
    async with get_db() as db:
        record = await get_sinistro_by_session(db, session_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Sinistro non trovato.")

    # GDPR Art. 5(2) — log operator access to sensitive claim data
    async with get_db() as audit_db:
        await log_accesso_dati_sensibili(
            audit_db,
            operator_id=current_operator.id,
            sinistro_id=record.id,
            azione="visualizzazione",
        )

    return {
        "id": record.id,
        "session_id": record.session_id,
        "operator_id": record.operator_id,
        "stato": record.stato,
        "claim_type": record.claim_type,
        "policyholder_name": record.policyholder_name,
        "codice_fiscale": record.codice_fiscale,
        "contact_method": record.contact_method,
        "policy_number": record.policy_number,
        "date_of_loss": record.date_of_loss,
        "loss_location": record.loss_location,
        "targa_veicolo": record.targa_veicolo,
        "provincia": record.provincia,
        "estimated_loss_eur": record.estimated_loss_eur,
        "claim_data_json": record.claim_data_json,
        "intake_packet_json": record.intake_packet_json,
        "transcript_json": record.transcript_json,
        "card_eligible": record.card_eligible,
        "consap_routing": record.consap_routing,
        "siu_flagged": record.siu_flagged,
        "siu_signals_json": record.siu_signals_json,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        "completed_at": record.completed_at.isoformat() if record.completed_at else None,
    }


@app.post("/api/sessions", response_model=SessionResponse)
async def create_session() -> SessionResponse:
    session = IntakeSession(session_id=str(uuid.uuid4()))
    # === FIX 3: Explicit session state reset ===
    session.normalized_claim = blank_claim()
    session.classification = None
    session.escalation_required = False
    session.escalation_reason = ""
    session.transcript = []
    session.transcript.append(
        {
            "speaker": "Agent",
            "text": "Buongiorno, sono Sofia, l'assistente virtuale per la raccolta sinistri. Sono qui per aiutarla ad avviare la sua pratica in modo semplice e veloce. Prima di tutto, lei e gli altri coinvolti state bene?",
        }
    )
    sessions[session.session_id] = session
    log_event("INFO", f"Nuova sessione: {session.session_id}", session_id=session.session_id, source="server.py:create_session")
    log_event("INFO", "Stato sinistro azzerato per nuova sessione", session.session_id)

    # Persist to database
    async with get_db() as db:
        await create_sinistro(db, session_id=session.session_id)

    workflow = build_initial_workflow_state()
    session.normalized_claim = workflow["normalized_claim"]
    session.classification = workflow["claim_classification"]
    session.route = workflow["fraud_safety_gate"]["final_routing_decision"]
    state = _ui_state(
        session,
        workflow["field_validation"],
        workflow["coverage_evidence_decision"],
        workflow["document_checklist"],
        workflow["fraud_safety_gate"],
        workflow["claim_intake_packet"],
        [
            {
                "tone": "warning",
                "title": "Waiting for claimant facts",
                "detail": "The ADK graph is ready to process claimant facts.",
                "rule": "SESSION-001",
            }
        ],
    )
    return SessionResponse(
        session_id=session.session_id,
        model=MODEL,
        has_api_key=_has_api_key(),
        state=state,
    )


@app.post("/api/message", response_model=SessionResponse)
async def message(request: MessageRequest) -> SessionResponse:
    session = sessions.get(request.session_id)
    if session is None:
        # --- FIX: auto-create session instead of returning 404 ---
        log_event(
            "WARNING",
            f"Sessione non trovata: {request.session_id} — creo nuova sessione. "
            f"Chiavi esistenti: {list(sessions.keys())[:5]}",
            session_id=request.session_id,
            source="server.py:message",
        )
        session = IntakeSession(session_id=request.session_id)
        # === FIX 3: Explicit session state reset ===
        session.normalized_claim = blank_claim()
        session.classification = None
        session.escalation_required = False
        session.escalation_reason = ""
        session.transcript = []
        session.transcript.append(
            {
                "speaker": "Agent",
                "text": "Sessione non trovata — avvio nuova acquisizione...",
            }
        )
        sessions[request.session_id] = session
        log_event("INFO", "Stato sinistro azzerato per nuova sessione", request.session_id)
        async with get_db() as db:
            existing = await get_sinistro_by_session(db, request.session_id)
            if not existing:
                await create_sinistro(db, session_id=request.session_id)
        workflow = build_initial_workflow_state()
        session.normalized_claim = workflow["normalized_claim"]
        session.classification = workflow["claim_classification"]
        session.route = workflow["fraud_safety_gate"]["final_routing_decision"]
        log_event(
            "INFO",
            f"Nuova sessione creata automaticamente: {request.session_id}",
            session_id=request.session_id,
            source="server.py:message",
        )
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message text is required.")
    session.transcript.append({"speaker": "Claimant", "text": text})
    state = await _process_with_adk_graph(session, add_claimant_facing_reply=True)
    return SessionResponse(
        session_id=session.session_id,
        model=MODEL,
        has_api_key=_has_api_key(),
        state=state,
    )


@app.websocket("/ws/live")
async def live_voice(websocket: WebSocket) -> None:
    await websocket.accept()
    session_id = str(uuid.uuid4())
    session = IntakeSession(session_id=session_id)
    # === FIX 3: Explicit session state reset ===
    session.normalized_claim = blank_claim()
    session.classification = None
    session.escalation_required = False
    session.escalation_reason = ""
    session.transcript = []
    session.transcript.append(
        {
            "speaker": "Agent",
            "text": "Buongiorno, sono Sofia, l'assistente virtuale per la raccolta sinistri. Sono qui per aiutarla ad avviare la sua pratica in modo semplice e veloce. Prima di tutto, lei e gli altri coinvolti state bene?",
        }
    )
    sessions[session_id] = session
    active_ws_sessions[session_id] = websocket
    log_event("INFO", "Stato sinistro azzerato per nuova sessione", session_id)
    log_event("INFO", f"Nuova sessione WebSocket: {session_id}", session_id=session_id, source="server.py:live_voice")

    # Persist new sinistro to database
    async with get_db() as db:
        await create_sinistro(db, session_id=session_id)

    # GDPR consent gate — Art. 6(1)(b) / Art. 9
    async with get_db() as db:
        consent = await verifica_consenso(db, session_id)
    if not consent["has_consent"]:
        await websocket.send_json({
            "type": "consent_required",
            "message": (
                "Prima di procedere, è necessario il suo "
                "consenso al trattamento dei dati personali "
                "ai sensi del GDPR."
            ),
            "testo_consenso": TESTO_CONSENSO_TRATTAMENTO,
            "testo_sensibili": TESTO_CONSENSO_DATI_SENSIBILI,
            "versione": CONSENSO_VERSIONE,
        })
        # Wait for consent — client must POST /gdpr/consenso then reconnect
        # Do not proceed with voice session without lawful basis

    try:
        from google.genai import types
    except ImportError:
        await websocket.send_json(
            {"type": "error", "message": "Missing google-genai package. Run pip install -r requirements.txt."}
        )
        await websocket.close()
        return

    if not _has_api_key():
        await websocket.send_json(
            {
                "type": "error",
                "message": f"Missing GOOGLE_API_KEY. Add it to {APP_DIR / '.env'} and restart the backend.",
            }
        )
        await websocket.close()
        return

    await websocket.send_json(
        {
            "type": "session",
            "session_id": session_id,
            "model": LIVE_MODEL,
            "message": "Gemini Live voice session connected.",
        }
    )

    # Italian FNOL Voice Agent — Sofia
    # Versione: 1.0 — Mercato Italiano
    # Conforme a: IVASS, Codice delle Assicurazioni (D.Lgs. 209/2005)
    # Lingua: Italiano formale (registro Lei)
    system_instruction = """\
Sei Sofia, assistente virtuale per l'acquisizione sinistri di una compagnia 
assicurativa italiana. Il tuo compito è raccogliere le informazioni necessarie 
per avviare la pratica di denuncia sinistro (FNOL) attraverso una conversazione 
vocale naturale e professionale.

Ti presenti così alla prima interazione:
"Buongiorno, sono Sofia, l'assistente virtuale per la raccolta sinistri. 
Sono qui per aiutarla ad avviare la sua pratica in modo semplice e veloce."

═══════════════════════════════════════════════════════════════
REGISTRO LINGUISTICO
═══════════════════════════════════════════════════════════════

- Parla SEMPRE in italiano, anche se l'assicurato parla in inglese.
  Eccezione: se l'assicurato parla inglese e sembra in forte difficoltà 
  emotiva, passa all'inglese e segnala la necessità di un operatore umano.
- Usa SEMPRE il registro formale "Lei" (mai "tu").
  Esempio corretto: "Come posso aiutarla?" — Mai: "Come posso aiutarti?"
- Usa italiano standard, mai dialetti regionali.
- Evita gergo tecnico-giuridico con l'assicurato. Usa termini semplici:
  "data del sinistro" (non "data di accadimento"),
  "sinistro" (non "claim"), "polizza" (non "policy"),
  "assicurato" (non "claimant"), "liquidatore" (non "adjuster"),
  "denuncia" (non "report"), "danno" (non "damage/loss").
- Numeri: formato italiano. Date: "il quindici marzo" o "15/03".
- Valuta: dire "euro", mai "EUR".
- Frasi brevi. Non elencare punti numerati. Conversa naturalmente.

═══════════════════════════════════════════════════════════════
INFORMAZIONI DA RACCOGLIERE (ordine naturale di priorità)
═══════════════════════════════════════════════════════════════

Raccogli queste informazioni attraverso la conversazione, non come 
un modulo. Ascolta, fai domande di approfondimento, adattati a ciò 
che l'assicurato comunica spontaneamente.

1. TIPO DI SINISTRO — Cosa è successo?
   Non chiedere "che tipo di sinistro è". Chiedi "Cosa è successo?" 
   e classifica la risposta (RC auto, furto, incendio, allagamento, 
   infortuni, responsabilità civile, ecc.).

2. DATA E LUOGO — Quando e dove?
   "Quando è successo?" → data
   "In che zona si trovava?" → via, comune, provincia

3. ANAGRAFICA — Chi è l'assicurato?
   "Mi può dire il suo nome e cognome?"
   "Il suo codice fiscale, se ce l'ha a portata di mano?"
   "Come preferisce essere ricontattato? Telefono o email?"

4. POLIZZA — Identificazione della polizza
   "Ha con sé il numero di polizza o un documento assicurativo?"
   Se non ce l'ha: "Non si preoccupi, lo recuperiamo noi."

5. DESCRIZIONE DEL DANNO — Dettagli specifici per tipo:
   - RC auto: "Ha compilato il modulo CAI/CID con l'altra parte?"
   - Furto: "Ha già sporto denuncia alle autorità?"
   - Allagamento: "Il danno è limitato al suo appartamento o 
     coinvolge anche altri condomini?"
   - Infortuni: "Ha già consultato un medico?"

6. VEICOLO (solo sinistri auto) —
   "Mi può dare la targa del veicolo coinvolto?"

7. STIMA DEL DANNO —
   "Ha già un'idea approssimativa dell'entità del danno?"
   "In euro, se possibile."

8. SICUREZZA E LESIONI —
   "Lei e gli altri coinvolti state bene? Ci sono lesioni?"
   Se ci sono lesioni: procedi IMMEDIATAMENTE con l'escalation 
   (vedi sezione ESCALATION).

9. EVIDENZE —
   "Ha fatto delle fotografie al danno?"
   "Ha dei testimoni? Ha ottenuto i dati dell'altra parte?"

10. DOCUMENTI DISPONIBILI — Chiedi in base al tipo di sinistro:
    - RC auto: "Ha il modulo CAI/CID o un verbale delle forze 
      dell'ordine?"
    - Furto: "Ha la copia della denuncia?"
    - Infortuni: "Ha un referto medico o un certificato?"

═══════════════════════════════════════════════════════════════
STILE DI CONVERSAZIONE
═══════════════════════════════════════════════════════════════

EMPATIA PRIMA DI TUTTO: quando l'assicurato descrive un evento 
traumatico (incidente, incendio, alluvione, furto), riconosci 
SEMPRE la situazione prima di fare domande:
  "Mi dispiace molto per quanto le è capitato. 
   Siamo qui per aiutarla."
  "Capisco, deve essere stato uno shock. 
   Cerchiamo di risolvere tutto il prima possibile."

MAI avere fretta: se l'assicurato è agitato o confuso, rallenta:
  "Si prenda il tempo che le serve. Sono qui."
  "Non si preoccupi, andiamo con calma."

MAI fare due domande insieme. Una domanda alla volta.

CONFERMA ciò che hai capito prima di proseguire:
  "Quindi, se ho capito bene: incidente stradale il 15 marzo 
   a Milano, con danni al veicolo. È corretto?"

GESTISCI IL SILENZIO con grazia:
  Se l'assicurato tace: "È ancora in linea? 
  Sono qui quando è pronto."

TRANSIZIONI naturali tra argomenti:
  "Grazie. Adesso ho bisogno di qualche informazione 
   sulla sua polizza..."

═══════════════════════════════════════════════════════════════
ESCALATION (CRITICO)
═══════════════════════════════════════════════════════════════

In questi casi, pronuncia ESATTAMENTE queste frasi e INTERROMPI 
la raccolta dati:

Se ci sono LESIONI:
  "La sua sicurezza è la priorità assoluta. 
   Se ha bisogno di assistenza medica immediata, 
   chiami il 118. 
   Trasferisco ora la sua chiamata a un operatore umano 
   che potrà supportarla meglio."

Se l'immobile è INAGIBILE (incendio, alluvione, danni strutturali):
  "Capisco che la situazione è urgente. 
   Attivo subito il servizio di pronto intervento 
   della compagnia. Un operatore la ricontatterà 
   entro 30 minuti per l'assistenza alloggiativa."

Se l'assicurato sembra in FORTE DIFFICOLTÀ o CRISI:
  "Capisco che questo è un momento difficile. 
   Passo la chiamata a un nostro operatore adesso."

═══════════════════════════════════════════════════════════════
FRASI VIETATE — Non dire MAI queste frasi o equivalenti:
═══════════════════════════════════════════════════════════════

MAI: "La sua polizza copre questo danno"
MAI: "Riceverà un risarcimento di X euro"
MAI: "È colpa dell'altra parte"
MAI: "La sua richiesta sarà accettata"
MAI: "Il sinistro è valido"

Invece, di' sempre:
  "Acquisisco tutte le informazioni e le trasmetterò 
   al liquidatore per la valutazione."
  "Sarà il liquidatore a valutare la copertura 
   e l'eventuale indennizzo."

═══════════════════════════════════════════════════════════════
SISTEMA CARD E CONSAP
═══════════════════════════════════════════════════════════════

Per sinistri RC auto con risarcimento diretto CARD:
  "Per i sinistri RC auto, la nostra compagnia gestisce 
   direttamente la sua pratica attraverso il sistema 
   di risarcimento diretto CARD. 
   Non dovrà contattare la compagnia dell'altro veicolo."

Per veicolo non assicurato o pirata della strada (CONSAP):
  "In questo caso, il sinistro potrebbe essere gestito 
   attraverso il Fondo di Garanzia Vittime della Strada, 
   gestito da CONSAP. 
   Le fornirò i dettagli a fine chiamata."

═══════════════════════════════════════════════════════════════
INFORMAZIONI MANCANTI
═══════════════════════════════════════════════════════════════

Se l'assicurato non ha un documento o un'informazione:
  "Non si preoccupi. Lo potrà inviare in un secondo momento 
   alla nostra email sinistri@compagnia.it oppure 
   attraverso l'app della compagnia."

Se non conosce il numero di polizza:
  "Va bene. Possiamo recuperarlo con il suo nome e 
   codice fiscale. Me lo può fornire?"

═══════════════════════════════════════════════════════════════
CHIUSURA DELLA PRATICA
═══════════════════════════════════════════════════════════════

Quando hai raccolto le informazioni critiche, riepilogale:
  "Bene. Ricapitolo quanto raccolto:
   [Riepilogo di: tipo sinistro, data, luogo, nome, polizza]
   È tutto corretto?"

Poi comunica i prossimi passi:
  "Entro i prossimi giorni lavorativi sarà contattato dal 
   liquidatore assegnato alla sua pratica.
   Ha domande prima di concludere?"

Disclaimer legale (da pronunciare alla fine):
  "Le ricordo che questa comunicazione non costituisce 
   riconoscimento di responsabilità né impegno di 
   indennizzo da parte della compagnia assicuratrice, 
   ai sensi del Codice delle Assicurazioni Private."

Chiusura finale:
  "Grazie per averci contattato. 
   Siamo dispiaciuti per l'accaduto e faremo il possibile 
   per assisterla. Buona giornata."
"""

    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        system_instruction=system_instruction,
        speech_config=types.SpeechConfig(
            language_code="it-IT",
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Leda")
            ),
        ),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )

    state_lock = asyncio.Lock()
    background_tasks: set[asyncio.Task] = set()

    def schedule_state_update(text: str) -> None:
        task = asyncio.create_task(update_claim_state(text))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

    async def update_claim_state(text: str) -> None:
        if not text.strip():
            return
        async with state_lock:
            session.transcript.append({"speaker": "Claimant", "text": text.strip()})
            try:
                state = await _process_with_adk_graph(session, add_claimant_facing_reply=False)
                await websocket.send_json({"type": "state", "state": state})

                # Flag session for escalation — NEVER close the WebSocket
                if (
                    state.get("route") == "emergency_escalation"
                    and not session.escalation_required
                ):
                    session.escalation_required = True
                    session.escalation_reason = "lesioni_personali"
                    await websocket.send_json({
                        "type": "escalation_flag",
                        "reason": "lesioni_personali",
                        "message": "Operatore umano notificato — pratica continua",
                    })
                    log_event(
                        "WARNING",
                        f"Escalation: {session.escalation_reason}",
                        session_id=session_id,
                        source="server.py:update_claim_state",
                    )

                # Persist claim data and transcript turn to database
                async with get_db() as db:
                    sinistro = await get_sinistro_by_session(db, session_id)
                    if sinistro:
                        claim_data = session.normalized_claim or {}
                        intake_packet = session.classification or {}
                        await update_sinistro_claim_data(
                            db,
                            session_id=session_id,
                            claim_data=claim_data,
                            intake_packet=intake_packet,
                            stato="in_acquisizione",
                        )
                        await add_transcript_turn(
                            db, sinistro.id,
                            ruolo="assicurato",
                            testo=text.strip(),
                        )
            except Exception as exc:
                log_event("ERROR", f"Aggiornamento stato sinistro fallito: {exc}", session_id=session_id, source="server.py:update_claim_state")
                await websocket.send_json({"type": "error", "message": f"Claim state update failed: {exc}"})

    try:
        async with _client().aio.live.connect(model=LIVE_MODEL, config=config) as live_session:
            async def client_to_gemini() -> None:
                while True:
                    message = await websocket.receive_json()
                    msg_type = message.get("type")
                    if msg_type == "audio":
                        data = base64.b64decode(message["data"])
                        await live_session.send_realtime_input(
                            audio=types.Blob(data=data, mime_type="audio/pcm;rate=16000")
                        )
                    elif msg_type == "text":
                        text = str(message.get("text", "")).strip()
                        if text:
                            session.transcript.append({"speaker": "Claimant", "text": text})
                            await live_session.send(input=text, end_of_turn=True)
                            state = await _process_with_adk_graph(session, add_claimant_facing_reply=False)
                            await websocket.send_json({"type": "state", "state": state})
                    elif msg_type == "close":
                        await websocket.close()
                        return

            async def gemini_to_client() -> None:
                pending_input = ""
                pending_output = ""

                async def finalize_input(reason: str) -> None:
                    nonlocal pending_input
                    finished = pending_input.strip()
                    if not finished:
                        return
                    pending_input = ""
                    await websocket.send_json(
                        {
                            "type": "transcript",
                            "speaker": "Claimant",
                            "text": finished,
                            "final": True,
                            "reason": reason,
                        }
                    )
                    schedule_state_update(finished)

                async def finalize_output(reason: str) -> None:
                    nonlocal pending_output
                    finished = pending_output.strip()
                    if not finished:
                        return
                    pending_output = ""
                    session.transcript.append({"speaker": "Agent", "text": finished})
                    await websocket.send_json(
                        {
                            "type": "transcript",
                            "speaker": "Agent",
                            "text": finished,
                            "final": True,
                            "reason": reason,
                        }
                    )
                    # Persist agent transcript turn to database
                    async with get_db() as db:
                        sinistro = await get_sinistro_by_session(db, session_id)
                        if sinistro:
                            await add_transcript_turn(
                                db, sinistro.id,
                                ruolo="agente",
                                testo=finished,
                            )

                while True:
                    turn = live_session.receive()
                    async for response in turn:
                        server_content = response.server_content
                        if not server_content:
                            continue

                        if server_content.input_transcription and server_content.input_transcription.text:
                            text = server_content.input_transcription.text
                            pending_input += text
                            await websocket.send_json(
                                {
                                    "type": "transcript",
                                    "speaker": "Claimant",
                                    "text": pending_input,
                                    "delta": text,
                                    "final": bool(getattr(server_content.input_transcription, "finished", False)),
                                }
                            )
                            if getattr(server_content.input_transcription, "finished", False):
                                await finalize_input("input_transcription_finished")

                        if server_content.output_transcription and server_content.output_transcription.text:
                            await finalize_input("model_started_response")
                            text = server_content.output_transcription.text
                            pending_output += text
                            await websocket.send_json(
                                {
                                    "type": "transcript",
                                    "speaker": "Agent",
                                    "text": pending_output,
                                    "delta": text,
                                    "final": bool(getattr(server_content.output_transcription, "finished", False)),
                                }
                            )
                            if getattr(server_content.output_transcription, "finished", False):
                                await finalize_output("output_transcription_finished")

                        if server_content.model_turn:
                            await finalize_input("model_audio_started")
                            for part in server_content.model_turn.parts or []:
                                if part.inline_data and isinstance(part.inline_data.data, bytes):
                                    await websocket.send_json(
                                        {
                                            "type": "audio",
                                            "data": base64.b64encode(part.inline_data.data).decode("ascii"),
                                            "mime_type": part.inline_data.mime_type or "audio/pcm;rate=24000",
                                        }
                                    )

                        if server_content.interrupted:
                            pending_output = ""
                            await websocket.send_json({"type": "interrupted"})

                        if (
                            getattr(server_content, "generation_complete", False)
                            or getattr(server_content, "turn_complete", False)
                            or getattr(server_content, "waiting_for_input", False)
                        ):
                            await finalize_output("live_turn_complete")

            tasks = {
                asyncio.create_task(client_to_gemini()),
                asyncio.create_task(gemini_to_client()),
            }
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
            for task in pending:
                with contextlib.suppress(asyncio.CancelledError):
                    await task
            for task in done:
                task.result()
    except WebSocketDisconnect:
        log_event("INFO", f"Sessione disconnessa: {session_id}", session_id=session_id, source="server.py:live_voice")
        return
    except Exception as exc:
        log_event("ERROR", f"Gemini Live sessione fallita: {exc}", session_id=session_id, source="server.py:live_voice")
        try:
            await websocket.send_json({"type": "error", "message": f"Gemini Live session failed: {exc}"})
        except Exception:
            pass
    finally:
        for task in list(background_tasks):
            task.cancel()
        for task in list(background_tasks):
            with contextlib.suppress(asyncio.CancelledError):
                await task
        # === FIX 3: Cleanup session and WebSocket state ===
        sessions.pop(session_id, None)
        active_ws_sessions.pop(session_id, None)
        log_event("INFO", "Sessione e stato sinistro rimossi dalla memoria", session_id)
        log_event("INFO", f"Sessione chiusa: {session_id}", session_id=session_id, source="server.py:live_voice")


# ---------------------------------------------------------------------------
# Monitoring endpoints
# ---------------------------------------------------------------------------


@app.get("/monitor")
def serve_monitor() -> FileResponse:
    """Serve the real-time monitoring dashboard."""
    return FileResponse(DEMO_DIR / "monitor.html")


@app.get("/api/monitor/stats")
def monitor_stats() -> dict[str, Any]:
    return {
        "sessioni_attive": len(active_ws_sessions),
        "sinistri_oggi": _sinistri_today(),
        "errori_ultima_ora": _errors_last_hour(),
        "quota_gemini_usata": _quota_today(),
        "quota_gemini_limite": 20,
        "uptime_secondi": int(time.time() - SERVER_START_TIME),
    }


@app.get("/api/monitor/logs")
def monitor_logs(
    limit: int = Query(100, ge=1, le=500),
    level: str = Query("all"),
) -> list[dict]:
    entries = list(LOG_BUFFER)
    if level.upper() != "ALL":
        entries = [e for e in entries if e["level"] == level.upper()]
    return entries[:limit]


@app.get("/api/monitor/sessions")
def monitor_sessions() -> list[dict]:
    now = datetime.now()
    result = []
    for sid, ws in active_ws_sessions.items():
        sess = sessions.get(sid)
        connected_at = now  # fallback
        duration = 0
        claim_type = "—"
        status = "collecting"
        last_activity = now.strftime("%H:%M:%S")
        if sess:
            if sess.classification and isinstance(sess.classification, dict):
                claim_type = sess.classification.get("claim_type", "—")
            if sess.escalation_required:
                status = "escalated"
            elif sess.route == "needs_docs":
                status = "collecting"
            elif sess.route in ("emergency_escalation",):
                status = "escalated"
            else:
                status = "collecting"
        result.append({
            "session_id": sid[:8],
            "full_session_id": sid,
            "connected_at": connected_at.strftime("%H:%M:%S"),
            "duration_seconds": duration,
            "claim_type": claim_type,
            "status": status,
            "last_activity": last_activity,
        })
    return result


@app.websocket("/ws/monitor")
async def ws_monitor(websocket: WebSocket) -> None:
    await websocket.accept()
    _monitor_ws_clients.add(websocket)
    log_event("INFO", "Monitor WebSocket connesso", source="server.py:ws_monitor")
    try:
        while True:
            # Keep connection alive; client sends pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        _monitor_ws_clients.discard(websocket)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(DEMO_DIR / "index.html")


app.mount("/", StaticFiles(directory=DEMO_DIR, html=True), name="static")
