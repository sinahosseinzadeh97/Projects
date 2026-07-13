"""Structured data contracts for the insurance claim intake workflow — Italian market."""

from __future__ import annotations

import re
from datetime import date, datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Italian claim types (rami assicurativi italiani)
# ---------------------------------------------------------------------------

ClaimType = Literal[
    "rc_auto",           # Responsabilità Civile Auto
    "kasko",             # Polizza Kasko / danni propri
    "furto_veicolo",     # Furto o tentato furto veicolo
    "incendio",          # Incendio e scoppio
    "infortuni",         # Infortuni sul lavoro o personali
    "rc_generale",       # Responsabilità Civile Generale
    "tutela_legale",     # Tutela legale
    "cristalli",         # Rottura cristalli
    "acqua_condotta",    # Danni da acqua condotta
    "furto_casa",        # Furto abitazione
    "grandine",          # Grandine e agenti atmosferici
    "viaggio",           # Assicurazione viaggio
    "other",             # Altro / non classificato
]


# ---------------------------------------------------------------------------
# Italian document types (documenti richiesti per la pratica)
# ---------------------------------------------------------------------------

class ItalianDocumentType(str, Enum):
    """Enumeration of documents commonly required in Italian claim handling."""

    denuncia_di_sinistro = "denuncia_di_sinistro"
    modulo_cai_cid = "modulo_cai_cid"            # Constatazione Amichevole di Incidente
    verbale_polizia = "verbale_polizia"            # Verbale delle autorità
    verbale_carabinieri = "verbale_carabinieri"
    fattura_riparazione = "fattura_riparazione"
    preventivo_riparazione = "preventivo_riparazione"
    referto_medico = "referto_medico"
    denuncia_furto = "denuncia_furto"              # Denuncia alle autorità per furto
    foto_danni = "foto_danni"
    relazione_perito = "relazione_perito"
    atto_di_citazione = "atto_di_citazione"        # Per contenziosi / tutela legale


# ---------------------------------------------------------------------------
# Italian claim disposition / stato della pratica
# ---------------------------------------------------------------------------

class ItalianClaimStatus(str, Enum):
    """Claim processing status used by Italian insurers."""

    in_acquisizione = "in_acquisizione"            # In fase di acquisizione dati
    in_attesa_documenti = "in_attesa_documenti"    # In attesa della documentazione
    in_lavorazione = "in_lavorazione"              # In lavorazione presso l'ufficio sinistri
    in_perizia = "in_perizia"                      # Perizia in corso
    definito = "definito"                          # Sinistro definito / liquidato
    rigettato = "rigettato"                        # Sinistro rigettato
    sospeso_siu = "sospeso_siu"                    # Sospeso per indagine antifrode (SIU)


# ---------------------------------------------------------------------------
# Existing literals (preserved)
# ---------------------------------------------------------------------------

Severity = Literal["low", "medium", "high", "urgent"]
IntakeStatus = Literal["valid", "missing_info"]
RoutingDecision = Literal[
    "ready_for_adjuster",
    "needs_docs",
    "special_investigation",
    "emergency_escalation",
]


# ---------------------------------------------------------------------------
# Helpers — Italian date format (DD/MM/YYYY)
# ---------------------------------------------------------------------------

_ITALIAN_DATE_RE = re.compile(r"^\d{2}/\d{2}/\d{4}$")


def parse_italian_date(value: str) -> date:
    """Parse a DD/MM/YYYY string into a :class:`datetime.date`."""
    return datetime.strptime(value, "%d/%m/%Y").date()


# ---------------------------------------------------------------------------
# ClaimNarrative — enriched with Italian-specific fields
# ---------------------------------------------------------------------------

class ClaimNarrative(BaseModel):
    """Normalized facts extracted from a messy claim narrative (Italian market)."""

    # ── Identity & policy ──────────────────────────────────────────────
    policyholder_name: str = Field(
        description="Nome e cognome dell'assicurato o del contraente."
    )
    policy_number: str = Field(
        description="Numero di polizza, se fornito."
    )
    numero_polizza: Optional[str] = Field(
        default=None,
        description="Numero di polizza (alias italiano).",
    )
    codice_fiscale: Optional[str] = Field(
        default=None,
        description="Codice Fiscale dell'assicurato (16 caratteri alfanumerici).",
    )
    contact_method: str = Field(
        description="Telefono, e-mail o indirizzo postale preferito."
    )

    # ── Vehicle-specific (RC Auto / Kasko / Furto veicolo) ─────────────
    targa_veicolo: Optional[str] = Field(
        default=None,
        description="Targa del veicolo coinvolto (formato italiano, es. AB123CD).",
    )

    # ── Claim identifiers ─────────────────────────────────────────────
    numero_sinistro: Optional[str] = Field(
        default=None,
        description="Numero di sinistro assegnato dalla compagnia.",
    )

    # ── Dates ──────────────────────────────────────────────────────────
    date_of_loss: str = Field(
        description="Data o intervallo di date in cui si è verificato il sinistro."
    )
    date_of_loss_italian: Optional[str] = Field(
        default=None,
        description=(
            "Data del sinistro in formato italiano DD/MM/YYYY. "
            "Se compilato, deve rispettare il formato GG/MM/AAAA."
        ),
    )
    reported_date: str = Field(
        description="Data in cui il sinistro è stato denunciato, se indicata."
    )
    reported_date_italian: Optional[str] = Field(
        default=None,
        description="Data di denuncia in formato italiano DD/MM/YYYY.",
    )

    # ── Location (Italian geography) ──────────────────────────────────
    loss_location: str = Field(
        description="Indirizzo, intersezione, comune o luogo del sinistro."
    )
    provincia: Optional[str] = Field(
        default=None,
        description="Provincia italiana (codice a 2 lettere, es. MI, RM, NA).",
    )
    comune: Optional[str] = Field(
        default=None,
        description="Nome del Comune.",
    )
    cap: Optional[str] = Field(
        default=None,
        description="Codice di Avviamento Postale (5 cifre).",
    )

    # ── Auto-specific Italian forms ───────────────────────────────────
    codice_cid: Optional[str] = Field(
        default=None,
        description="Numero del modulo CAI/CID (Constatazione Amichevole di Incidente).",
    )
    numero_verbale_polizia: Optional[str] = Field(
        default=None,
        description="Numero del verbale delle autorità (Polizia Stradale, Carabinieri).",
    )

    # ── Narrative & financials ────────────────────────────────────────
    loss_description: str = Field(
        description="Descrizione sintetica dell'accaduto."
    )
    estimated_loss_eur: Optional[float] = Field(
        default=None,
        description="Stima del danno in EUR (€), se indicata.",
    )
    injuries_or_safety_concerns: list[str] = Field(default_factory=list)
    parties_involved: list[str] = Field(default_factory=list)
    evidence_available: list[str] = Field(default_factory=list)
    documents_mentioned: list[str] = Field(default_factory=list)
    missing_or_uncertain_facts: list[str] = Field(default_factory=list)
    raw_narrative_summary: str = Field(
        description="Riepilogo fattuale breve della narrazione originale."
    )
    assumptions: list[str] = Field(default_factory=list)

    # ── Validators ────────────────────────────────────────────────────

    @field_validator("codice_fiscale")
    @classmethod
    def _validate_codice_fiscale(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.upper().strip()
        if not re.fullmatch(r"[A-Z0-9]{16}", v):
            raise ValueError(
                "Il Codice Fiscale deve essere composto da 16 caratteri alfanumerici."
            )
        return v

    @field_validator("targa_veicolo")
    @classmethod
    def _validate_targa_veicolo(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.upper().strip().replace(" ", "")
        # Formato targhe italiane dal 1994: AA 000 AA
        if not re.fullmatch(r"[A-Z]{2}\d{3}[A-Z]{2}", v):
            raise ValueError(
                "La targa deve essere nel formato italiano (es. AB123CD)."
            )
        return v

    @field_validator("cap")
    @classmethod
    def _validate_cap(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not re.fullmatch(r"\d{5}", v):
            raise ValueError("Il CAP deve essere composto da esattamente 5 cifre.")
        return v

    @field_validator("provincia")
    @classmethod
    def _validate_provincia(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.upper().strip()
        if not re.fullmatch(r"[A-Z]{2}", v):
            raise ValueError(
                "La provincia deve essere un codice di 2 lettere maiuscole (es. MI, RM)."
            )
        return v

    @field_validator("date_of_loss_italian", "reported_date_italian")
    @classmethod
    def _validate_italian_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Ensure Italian date strings match DD/MM/YYYY."""
        if v is None:
            return v
        v = v.strip()
        if not _ITALIAN_DATE_RE.fullmatch(v):
            raise ValueError(
                "La data deve essere nel formato DD/MM/YYYY (es. 25/12/2025)."
            )
        # Validate it's actually a real date
        try:
            parse_italian_date(v)
        except ValueError:
            raise ValueError(f"La data '{v}' non è una data valida.")
        return v


# ---------------------------------------------------------------------------
# FieldValidation (preserved)
# ---------------------------------------------------------------------------

class FieldValidation(BaseModel):
    """Deterministic validation of minimum claim intake information."""

    intake_status: IntakeStatus
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    ready_for_policy_review: bool


# ---------------------------------------------------------------------------
# ClaimClassification (updated for Italian claim types)
# ---------------------------------------------------------------------------

class ClaimClassification(BaseModel):
    """LLM classification of claim type and operational severity."""

    claim_type: ClaimType
    severity: Severity
    severity_rationale: str
    likely_policy_line: str = Field(
        description="Ramo assicurativo più probabile (es. RCA, ARD, Kasko, Incendio)."
    )
    loss_drivers: list[str] = Field(default_factory=list)
    claimant_needs: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# EvidenceRuleFinding (preserved)
# ---------------------------------------------------------------------------

class EvidenceRuleFinding(BaseModel):
    """Deterministic finding generated by coverage, evidence, or routing rules."""

    rule_id: str
    severity: Severity
    message: str
    required_action: Literal[
        "collect_info",
        "collect_document",
        "adjuster_review",
        "siu_review",
        "emergency_escalation",
    ]
    document: Optional[str] = None


# ---------------------------------------------------------------------------
# CoverageEvidenceDecision (preserved)
# ---------------------------------------------------------------------------

class CoverageEvidenceDecision(BaseModel):
    """Deterministic routing output after coverage and evidence gates."""

    routing_decision: RoutingDecision
    provisional_coverage_considerations: list[str] = Field(default_factory=list)
    required_documents: list[str] = Field(default_factory=list)
    findings: list[EvidenceRuleFinding] = Field(default_factory=list)
    audit_trail: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# DocumentChecklistItem & DocumentChecklist (preserved + Italian doc type)
# ---------------------------------------------------------------------------

class DocumentChecklistItem(BaseModel):
    """One claimant-facing checklist item."""

    item: str
    reason: str
    priority: Literal["required", "recommended", "conditional"]
    already_provided: bool = False
    italian_document_type: Optional[ItalianDocumentType] = Field(
        default=None,
        description="Tipo di documento italiano corrispondente, se applicabile.",
    )


class DocumentChecklist(BaseModel):
    """Generated document checklist for the claim packet."""

    items: list[DocumentChecklistItem] = Field(default_factory=list)
    claimant_tip: str


# ---------------------------------------------------------------------------
# FraudSafetySignal & FraudSafetyGate (preserved)
# ---------------------------------------------------------------------------

class FraudSafetySignal(BaseModel):
    """Deterministic SIU, fraud-pattern, and safety signal."""

    signal_id: str
    severity: Severity
    message: str
    route_to_siu: bool = False
    route_to_emergency: bool = False


class FraudSafetyGate(BaseModel):
    """Final deterministic safety and fraud routing gate."""

    final_routing_decision: RoutingDecision
    signals: list[FraudSafetySignal] = Field(default_factory=list)
    audit_trail: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# ClaimIntakePacket — original final packet (preserved, updated for Italy)
# ---------------------------------------------------------------------------

class ClaimIntakePacket(BaseModel):
    """Final polished packet returned to ADK Web (Italian market)."""

    claim_type: ClaimType
    intake_status: IntakeStatus
    severity: Severity
    routing_decision: RoutingDecision
    stato_sinistro: ItalianClaimStatus = Field(
        default=ItalianClaimStatus.in_acquisizione,
        description="Stato corrente della pratica secondo il flusso italiano.",
    )
    missing_information: list[str] = Field(default_factory=list)
    required_documents: list[DocumentChecklistItem] = Field(default_factory=list)
    coverage_considerations: list[str] = Field(default_factory=list)
    adjuster_handoff_summary: str
    claimant_next_message: str
    audit_trail: list[str] = Field(default_factory=list)
    markdown: str


# ---------------------------------------------------------------------------
# ClaimPacketIta — complete adjuster-ready handoff for Italian market
# ---------------------------------------------------------------------------

class ClaimPacketIta(BaseModel):
    """
    Pacchetto completo per la cessione al liquidatore / perito.

    Raccoglie tutti i dati raccolti durante l'acquisizione del sinistro,
    i documenti richiesti/mancanti e un riepilogo in lingua italiana.
    """

    # ── Identity & Policy ─────────────────────────────────────────────
    policyholder_name: str = Field(description="Nome e cognome dell'assicurato.")
    codice_fiscale: Optional[str] = Field(
        default=None,
        description="Codice Fiscale dell'assicurato.",
    )
    numero_polizza: Optional[str] = Field(
        default=None,
        description="Numero di polizza.",
    )
    contact_method: str = Field(description="Recapito preferito.")

    # ── Claim identifiers ─────────────────────────────────────────────
    numero_sinistro: Optional[str] = Field(
        default=None,
        description="Numero di sinistro assegnato dalla compagnia.",
    )

    # ── Claim classification ──────────────────────────────────────────
    claim_type: ClaimType
    severity: Severity
    severity_rationale: str = Field(
        description="Motivazione della gravità assegnata."
    )

    # ── Dates ──────────────────────────────────────────────────────────
    date_of_loss: str
    date_of_loss_italian: Optional[str] = Field(
        default=None,
        description="Data del sinistro in formato DD/MM/YYYY.",
    )
    reported_date: str
    reported_date_italian: Optional[str] = Field(
        default=None,
        description="Data di denuncia in formato DD/MM/YYYY.",
    )

    # ── Location ──────────────────────────────────────────────────────
    loss_location: str
    provincia: Optional[str] = None
    comune: Optional[str] = None
    cap: Optional[str] = None

    # ── Vehicle / Auto ────────────────────────────────────────────────
    targa_veicolo: Optional[str] = None
    codice_cid: Optional[str] = None
    numero_verbale_polizia: Optional[str] = None

    # ── Financials ────────────────────────────────────────────────────
    estimated_loss_eur: Optional[float] = Field(
        default=None,
        description="Stima del danno in EUR (€).",
    )

    # ── Narrative ─────────────────────────────────────────────────────
    loss_description: str
    injuries_or_safety_concerns: list[str] = Field(default_factory=list)
    parties_involved: list[str] = Field(default_factory=list)

    # ── Status & Routing ──────────────────────────────────────────────
    stato_sinistro: ItalianClaimStatus = Field(
        default=ItalianClaimStatus.in_acquisizione,
    )
    routing_decision: RoutingDecision
    intake_status: IntakeStatus

    # ── Documents ─────────────────────────────────────────────────────
    required_documents: list[DocumentChecklistItem] = Field(default_factory=list)
    missing_documents: list[ItalianDocumentType] = Field(
        default_factory=list,
        description="Elenco dei documenti italiani ancora mancanti per completare la pratica.",
    )
    evidence_available: list[str] = Field(default_factory=list)

    # ── Coverage & Fraud ──────────────────────────────────────────────
    coverage_considerations: list[str] = Field(default_factory=list)
    fraud_safety_signals: list[FraudSafetySignal] = Field(default_factory=list)

    # ── Summaries ─────────────────────────────────────────────────────
    riepilogo_italiano: str = Field(
        description=(
            "Riepilogo in lingua italiana del sinistro, pronto per il liquidatore. "
            "Deve contenere: tipo sinistro, data, luogo, descrizione, "
            "importo stimato, documenti mancanti e prossimi passi."
        ),
    )
    adjuster_handoff_summary: str = Field(
        description="English-language adjuster handoff summary (for bilingual systems).",
    )
    claimant_next_message: str = Field(
        description="Messaggio da inviare all'assicurato con i prossimi passi.",
    )

    # ── Audit ─────────────────────────────────────────────────────────
    audit_trail: list[str] = Field(default_factory=list)
    markdown: str = Field(
        description="Markdown-formatted claim packet for display.",
    )

    # ── Validators (same rules as ClaimNarrative) ─────────────────────

    @field_validator("codice_fiscale")
    @classmethod
    def _validate_codice_fiscale(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.upper().strip()
        if not re.fullmatch(r"[A-Z0-9]{16}", v):
            raise ValueError(
                "Il Codice Fiscale deve essere composto da 16 caratteri alfanumerici."
            )
        return v

    @field_validator("targa_veicolo")
    @classmethod
    def _validate_targa_veicolo(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.upper().strip().replace(" ", "")
        if not re.fullmatch(r"[A-Z]{2}\d{3}[A-Z]{2}", v):
            raise ValueError(
                "La targa deve essere nel formato italiano (es. AB123CD)."
            )
        return v

    @field_validator("cap")
    @classmethod
    def _validate_cap(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not re.fullmatch(r"\d{5}", v):
            raise ValueError("Il CAP deve essere composto da esattamente 5 cifre.")
        return v

    @field_validator("provincia")
    @classmethod
    def _validate_provincia(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.upper().strip()
        if not re.fullmatch(r"[A-Z]{2}", v):
            raise ValueError(
                "La provincia deve essere un codice di 2 lettere maiuscole (es. MI, RM)."
            )
        return v

    @field_validator("date_of_loss_italian", "reported_date_italian")
    @classmethod
    def _validate_italian_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not _ITALIAN_DATE_RE.fullmatch(v):
            raise ValueError(
                "La data deve essere nel formato DD/MM/YYYY (es. 25/12/2025)."
            )
        try:
            parse_italian_date(v)
        except ValueError:
            raise ValueError(f"La data '{v}' non è una data valida.")
        return v
