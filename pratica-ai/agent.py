"""ADK hybrid graph workflow for AI Acquisizione Sinistri — PraticaAI — Italian market."""

from __future__ import annotations

import inspect
import json
import uuid
from typing import Any, AsyncGenerator, Callable

from google.adk.agents import BaseAgent, LlmAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.runners import Runner
from google.adk.sessions import Session
from google.genai import types as genai_types
from pydantic import BaseModel, ConfigDict
from typing_extensions import override

try:
    from .llm_provider import LLMProvider
    from .policies import (
        apply_coverage_and_evidence_rules,
        build_claim_intake_packet,
        fraud_signal_and_safety_gate,
        generate_document_checklist,
        validate_required_claim_fields,
    )
    from .schemas import (
        ClaimClassification,
        ClaimIntakePacket,
        ClaimNarrative,
        CoverageEvidenceDecision,
        DocumentChecklist,
        FieldValidation,
        FraudSafetyGate,
    )
except ImportError:
    from llm_provider import LLMProvider
    from policies import (
        apply_coverage_and_evidence_rules,
        build_claim_intake_packet,
        fraud_signal_and_safety_gate,
        generate_document_checklist,
        validate_required_claim_fields,
    )
    from schemas import (
        ClaimClassification,
        ClaimIntakePacket,
        ClaimNarrative,
        CoverageEvidenceDecision,
        DocumentChecklist,
        FieldValidation,
        FraudSafetyGate,
    )


# === FIX 2: LLM model from provider abstraction ===
MODEL = LLMProvider.get_extraction_model()


# === FIX 1: PostgreSQL-backed session service ===
class DatabaseSessionService:
    """Session service that persists state in the PostgreSQL sinistri table.

    Uses the existing ``claim_data_json`` column via :func:`database.get_db`
    so that session state survives server restarts.
    """

    def __init__(self) -> None:
        self._cache: dict[str, Session] = {}

    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        state: dict[str, Any] | None = None,
    ) -> Session:
        session = Session(
            app_name=app_name,
            user_id=user_id,
            id=session_id,
            state=state or {},
        )
        self._cache[session_id] = session
        # Persist initial state to database
        await self._persist(session_id, session.state)
        return session

    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> Session | None:
        if session_id in self._cache:
            return self._cache[session_id]
        # Try loading from database
        state = await self._load(session_id)
        if state is not None:
            session = Session(
                app_name=app_name,
                user_id=user_id,
                id=session_id,
                state=state,
            )
            self._cache[session_id] = session
            return session
        return None

    async def update_session(
        self,
        session_id: str,
        state: dict[str, Any],
    ) -> Session | None:
        session = self._cache.get(session_id)
        if session is None:
            return None
        session.state.update(state)
        await self._persist(session_id, session.state)
        return session

    async def delete_session(self, session_id: str) -> None:
        self._cache.pop(session_id, None)

    # --- internal helpers ---

    @staticmethod
    async def _persist(session_id: str, state: dict[str, Any]) -> None:
        """Write session state to the sinistri.claim_data_json column."""
        try:
            from database import get_db, get_sinistro_by_session, update_sinistro_claim_data

            # Strip the "claim-" prefix added by run_claim_workflow
            raw_sid = session_id.removeprefix("claim-")
            async with get_db() as db:
                record = await get_sinistro_by_session(db, raw_sid)
                if record is not None:
                    await update_sinistro_claim_data(
                        db,
                        session_id=raw_sid,
                        claim_data=state,
                    )
        except Exception:
            pass  # graceful degradation — session still works in-memory

    @staticmethod
    async def _load(session_id: str) -> dict[str, Any] | None:
        """Load session state from the sinistri.claim_data_json column."""
        try:
            from database import get_db, get_sinistro_by_session

            raw_sid = session_id.removeprefix("claim-")
            async with get_db() as db:
                record = await get_sinistro_by_session(db, raw_sid)
                if record is not None and record.claim_data_json:
                    return dict(record.claim_data_json)
        except Exception:
            pass
        return None
APP_NAME = "pratica_ai"


async def _await_if_needed(value: Any) -> Any:
    return await value if inspect.isawaitable(value) else value


def _plain(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(exclude_none=True)
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("{") or text.startswith("["):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return value
    return value


def blank_claim() -> dict[str, Any]:
    return {
        "policyholder_name": "non specificato",
        "policy_number": "non specificato",
        "contact_method": "non specificato",
        "date_of_loss": "non specificato",
        "reported_date": "non specificato",
        "loss_location": "non specificato",
        "loss_description": "non specificato",
        "estimated_loss_eur": None,
        "injuries_or_safety_concerns": [],
        "parties_involved": [],
        "evidence_available": [],
        "documents_mentioned": [],
        "missing_or_uncertain_facts": [],
        "raw_narrative_summary": "non specificato",
        "assumptions": [],
    }


def initial_classification() -> dict[str, Any]:
    return {
        "claim_type": "other",
        "severity": "medium",
        "severity_rationale": "In attesa dei dati dall'assicurato.",
        "likely_policy_line": "sconosciuto",
        "loss_drivers": [],
        "claimant_needs": ["Fornire i fatti iniziali del sinistro."],
    }


def build_initial_workflow_state() -> dict[str, Any]:
    claim = blank_claim()
    classification = initial_classification()
    validation = validate_required_claim_fields(claim)
    coverage = apply_coverage_and_evidence_rules(claim, validation, classification)
    checklist = generate_document_checklist(claim, classification, coverage)
    fraud_gate = fraud_signal_and_safety_gate(claim, validation, classification, coverage)
    packet = build_claim_intake_packet(
        claim,
        validation,
        classification,
        coverage,
        checklist,
        fraud_gate,
    )
    return {
        "normalized_claim": claim,
        "field_validation": validation,
        "claim_classification": classification,
        "coverage_evidence_decision": coverage,
        "document_checklist": checklist,
        "fraud_safety_gate": fraud_gate,
        "claim_intake_packet": packet,
        "final_markdown": packet["markdown"],
    }


def _content(text: str) -> genai_types.Content:
    return genai_types.Content(role="model", parts=[genai_types.Part(text=text)])


def _state_event(author: str, text: str, updates: dict[str, Any]) -> Event:
    return Event(
        author=author,
        content=_content(text),
        actions=EventActions(state_delta=updates),
    )


class FunctionNode(BaseAgent):
    """Deterministic workflow node that reads and writes ADK session state."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    handler: Callable[[InvocationContext], dict[str, Any]]
    output_key: str
    summary: str

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        result = self.handler(ctx)
        ctx.session.state[self.output_key] = result
        yield _state_event(self.name, self.summary, {self.output_key: result})


class FinalPacketNode(FunctionNode):
    """Function node that returns the final packet Markdown as ADK Web output."""

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        result = self.handler(ctx)
        updates = {self.output_key: result, "final_markdown": result["markdown"]}
        ctx.session.state.update(updates)
        yield _state_event(self.name, result["markdown"], updates)


def _validate_claim_handler(ctx: InvocationContext) -> dict[str, Any]:
    return validate_required_claim_fields(ctx.session.state.get("normalized_claim"))


def _coverage_evidence_handler(ctx: InvocationContext) -> dict[str, Any]:
    return apply_coverage_and_evidence_rules(
        ctx.session.state.get("normalized_claim"),
        ctx.session.state.get("field_validation"),
        ctx.session.state.get("claim_classification"),
    )


def _document_checklist_handler(ctx: InvocationContext) -> dict[str, Any]:
    return generate_document_checklist(
        ctx.session.state.get("normalized_claim"),
        ctx.session.state.get("claim_classification"),
        ctx.session.state.get("coverage_evidence_decision"),
    )


def _fraud_safety_handler(ctx: InvocationContext) -> dict[str, Any]:
    return fraud_signal_and_safety_gate(
        ctx.session.state.get("normalized_claim"),
        ctx.session.state.get("field_validation"),
        ctx.session.state.get("claim_classification"),
        ctx.session.state.get("coverage_evidence_decision"),
    )


def _final_packet_handler(ctx: InvocationContext) -> dict[str, Any]:
    return build_claim_intake_packet(
        ctx.session.state.get("normalized_claim"),
        ctx.session.state.get("field_validation"),
        ctx.session.state.get("claim_classification"),
        ctx.session.state.get("coverage_evidence_decision"),
        ctx.session.state.get("document_checklist"),
        ctx.session.state.get("fraud_safety_gate"),
    )


def create_normalizer() -> LlmAgent:
    return LlmAgent(
        name="NormalizeClaimNarrative",
        model=MODEL,
        description="Normalizza le narrazioni di sinistro in dati strutturati per il mercato assicurativo italiano.",
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
        instruction="""
Sei lo specialista di acquisizione sinistri per un Agente AI di Primo Avviso
di Sinistro (FNOL) nel mercato assicurativo italiano.

Leggi la narrazione del sinistro fornita dall'assicurato e produci un
ClaimNarrative strutturato. Preserva i fatti esattamente come forniti.
Non inventare numeri di polizza, contatti, date, luoghi, prove o importi.

Regole di estrazione:
- policyholder_name: nome e cognome dell'assicurato/contraente, altrimenti "non specificato".
- policy_number: numero di polizza, altrimenti "non specificato".
- numero_polizza: alias italiano del numero di polizza, se fornito.
- codice_fiscale: Codice Fiscale (16 caratteri alfanumerici), se menzionato.
- contact_method: telefono, email o indirizzo postale preferito, altrimenti "non specificato".
- targa_veicolo: targa del veicolo coinvolto (formato italiano, es. AB123CD), se applicabile.
- date_of_loss: data o intervallo di date del sinistro, altrimenti "non specificato".
- date_of_loss_italian: data del sinistro in formato DD/MM/YYYY, se fornita.
- reported_date: data di denuncia del sinistro, altrimenti "non specificato".
- reported_date_italian: data di denuncia in formato DD/MM/YYYY, se fornita.
- loss_location: indirizzo, comune, intersezione o luogo del sinistro, altrimenti "non specificato".
- provincia: codice provincia (2 lettere, es. MI, RM, NA), se menzionato.
- comune: nome del Comune, se menzionato.
- cap: CAP (5 cifre), se menzionato.
- codice_cid: numero del modulo CAI/CID (Constatazione Amichevole di Incidente), se menzionato.
- numero_verbale_polizia: numero del verbale delle autorità, se menzionato.
- loss_description: descrizione sintetica e fattuale dell'accaduto.
- estimated_loss_eur: stima del danno in EUR (€), solo se esplicitamente indicata.
- injuries_or_safety_concerns: lesioni personali, cure mediche urgenti, cervicalgia,
  colpo di frusta, abitazione non agibile, pericoli elettrici, allagamento, muffa.
- evidence_available: foto, video, ricevute, numeri di verbale, preventivi, fatture,
  referti medici, moduli CAI/CID o altre prove già menzionate.
- documents_mentioned: documenti specifici citati, disponibili o mancanti (denuncia,
  verbale, referto, fattura, preventivo, ecc.).
- missing_or_uncertain_facts: fatti che la narrazione indica come sconosciuti, vaghi o incompleti.

Questo è un passaggio di normalizzazione. Non confermare copertura, indennizzo o responsabilità.
""",
        output_schema=ClaimNarrative,
        output_key="normalized_claim",
    )


def create_classifier() -> LlmAgent:
    return LlmAgent(
        name="ClassifyClaimTypeAndSeverity",
        model=MODEL,
        description="Classifica il tipo di sinistro, la gravità, il ramo assicurativo e le esigenze dell'assicurato.",
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
        instruction="""
Classifica questo sinistro normalizzato per l'instradamento della pratica.

Sinistro normalizzato:
{normalized_claim}

Validazione:
{field_validation}

Tipi di sinistro supportati (rami assicurativi italiani):
- rc_auto: Responsabilità Civile Auto (tamponamento, incidente stradale)
- kasko: Polizza Kasko / danni propri al veicolo
- furto_veicolo: Furto o tentato furto del veicolo
- incendio: Incendio e scoppio
- infortuni: Infortuni sul lavoro o personali
- rc_generale: Responsabilità Civile Generale
- tutela_legale: Tutela legale / spese legali
- cristalli: Rottura cristalli (parabrezza, lunotto)
- acqua_condotta: Danni da acqua condotta / allagamento
- furto_casa: Furto in abitazione
- grandine: Grandine e agenti atmosferici
- viaggio: Assicurazione viaggio
- other: Altro / non classificato

Rubrica di gravità:
- low: pratica completa, importo contenuto, nessuna lesione/sicurezza, documentazione di routine.
- medium: documenti mancanti o complessità moderata.
- high: importo stimato elevato, responsabilità incerta, fatti essenziali mancanti, gestione specialistica probabile.
- urgent: lesioni personali, abitazione non agibile, emergenza medica/sicurezza, intervento urgente.

Per likely_policy_line, utilizza i rami assicurativi italiani: RCA, ARD, Kasko,
Incendio, Infortuni, RC Generale, Tutela Legale, Cristalli, Acqua Condotta,
Furto, Grandine, Viaggio, Altro.

Restituisci solo la classificazione strutturata ClaimClassification.
Questo è un passaggio di classificazione, non una decisione sulla copertura.
""",
        output_schema=ClaimClassification,
        output_key="claim_classification",
    )


def create_workflow() -> SequentialAgent:
    return SequentialAgent(
        name="pratica_ai",
        description="Team di agenti vocali per l'acquisizione sinistri, il triage documentale e l'instradamento — mercato assicurativo italiano.",
        sub_agents=[
            create_normalizer(),
            FunctionNode(
                name="ValidateRequiredClaimFields",
                description="Deterministically validates required claim intake fields.",
                handler=_validate_claim_handler,
                output_key="field_validation",
                summary="Validated required claim intake fields.",
            ),
            create_classifier(),
            FunctionNode(
                name="ApplyCoverageAndEvidenceRules",
                description="Applies deterministic coverage, evidence, severity, and routing gates.",
                handler=_coverage_evidence_handler,
                output_key="coverage_evidence_decision",
                summary="Applied deterministic coverage and evidence rules.",
            ),
            FunctionNode(
                name="GenerateDocumentChecklist",
                description="Builds a claimant-facing document checklist from deterministic rules.",
                handler=_document_checklist_handler,
                output_key="document_checklist",
                summary="Generated required document checklist.",
            ),
            FunctionNode(
                name="FraudSignalAndSafetyGate",
                description="Applies deterministic fraud signal, suspicious timing, and safety gates.",
                handler=_fraud_safety_handler,
                output_key="fraud_safety_gate",
                summary="Applied fraud, timing, and safety routing gates.",
            ),
            FinalPacketNode(
                name="FinalClaimIntakePacket",
                description="Builds the final polished Markdown claim intake packet.",
                handler=_final_packet_handler,
                output_key="claim_intake_packet",
                summary="Built final claim intake packet.",
            ),
        ],
    )


root_agent = create_workflow()


async def run_claim_workflow(
    claimant_transcript: str,
    *,
    session_id: str | None = None,
    user_id: str = "live-ui",
) -> dict[str, Any]:
    """Run the ADK claim graph for the current claimant transcript snapshot."""

    transcript = str(claimant_transcript or "").strip()
    if not transcript:
        return build_initial_workflow_state()

    adk_session_id = f"claim-{session_id or uuid.uuid4().hex}"
    session_service = DatabaseSessionService()
    await _await_if_needed(
        session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=adk_session_id,
        )
    )
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )
    message = genai_types.Content(
        role="user",
        parts=[
            genai_types.Part(
                text=(
                    "Utilizza questa trascrizione completa dell'assicurato come fonte "
                    "di verità per il flusso di acquisizione sinistro. "
                    "Non inventare fatti mancanti. Usa il formato italiano per date (DD/MM/YYYY) "
                    "e importi (EUR €).\n\n"
                    f"{transcript}"
                )
            )
        ],
    )

    event_count = 0
    async for _event in runner.run_async(
        user_id=user_id,
        session_id=adk_session_id,
        new_message=message,
    ):
        event_count += 1
    if event_count == 0:
        raise RuntimeError("ADK workflow completed without emitting any events.")

    session = await _await_if_needed(
        session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=adk_session_id,
        )
    )
    state = session.state
    claim = ClaimNarrative.model_validate(_plain(state.get("normalized_claim")))
    validation = FieldValidation.model_validate(_plain(state.get("field_validation")))
    classification = ClaimClassification.model_validate(_plain(state.get("claim_classification")))
    coverage = CoverageEvidenceDecision.model_validate(_plain(state.get("coverage_evidence_decision")))
    checklist = DocumentChecklist.model_validate(_plain(state.get("document_checklist")))
    fraud_gate = FraudSafetyGate.model_validate(_plain(state.get("fraud_safety_gate")))
    packet = ClaimIntakePacket.model_validate(_plain(state.get("claim_intake_packet")))
    return {
        "normalized_claim": claim.model_dump(exclude_none=True),
        "field_validation": validation.model_dump(exclude_none=True),
        "claim_classification": classification.model_dump(exclude_none=True),
        "coverage_evidence_decision": coverage.model_dump(exclude_none=True),
        "document_checklist": checklist.model_dump(exclude_none=True),
        "fraud_safety_gate": fraud_gate.model_dump(exclude_none=True),
        "claim_intake_packet": packet.model_dump(exclude_none=True),
        "final_markdown": packet.markdown,
    }


__all__ = [
    "APP_NAME",
    "MODEL",
    "blank_claim",
    "build_initial_workflow_state",
    "create_workflow",
    "run_claim_workflow",
    "root_agent",
]
