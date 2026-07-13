"""GDPR compliance layer for the Italian FNOL voice agent.

Implements:
- Art. 6  — Lawful basis for processing (contract performance)
- Art. 7  — Conditions for consent (recorded, versioned, revocable)
- Art. 9  — Processing of special category data (health/injury)
- Art. 13 — Information to be provided to the data subject
- Art. 17 — Right to erasure (diritto alla cancellazione)
- Art. 30 — Records of processing activities (ROPA)

Italian law references:
- D.Lgs. 196/2003 (Codice Privacy), as amended by D.Lgs. 101/2018
- IVASS Regulation 40/2018 (insurance data governance)
- Art. 2946 C.C. — 10-year prescription for insurance contracts

All personal-data operations are audit-logged.  IP addresses are
SHA-256 hashed before storage (never stored raw).
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth import get_current_operator, OperatorOut
from database import (
    AuditLogGDPR,
    ConsensoGDPR,
    Sinistro,
    TurnTranscript,
    get_db,
    get_sinistro_by_session,
)

# ---------------------------------------------------------------------------
# Constants — legal references baked in
# ---------------------------------------------------------------------------

CONSENSO_VERSIONE: str = "1.0-IT-2026"

RETENTION_SINISTRI_ANNI: int = 10
"""Art. 2946 C.C. — 10-year prescription for insurance contracts."""

RETENTION_AUDIO_GIORNI: int = 0
"""Never store raw audio — transcribe and delete immediately."""

TESTO_CONSENSO_TRATTAMENTO: str = (
    "I Suoi dati personali saranno trattati da [Nome Compagnia] "
    "in qualità di Titolare del Trattamento, ai sensi dell'art. "
    "6(1)(b) del GDPR, per l'esecuzione del contratto assicurativo "
    "e la gestione del sinistro. I dati potranno essere comunicati "
    "a periti, liquidatori, autorità competenti e riassicuratori. "
    "Ha diritto di accesso, rettifica, cancellazione e portabilità "
    "dei dati. Per esercitare i Suoi diritti: privacy@compagnia.it "
    "Informativa completa: www.compagnia.it/privacy "
    "Provvedimento del Garante n. [X] del [data]."
)

TESTO_CONSENSO_DATI_SENSIBILI: str = (
    "Il trattamento include dati particolari (dati sulla salute) "
    "ai sensi dell'art. 9 GDPR, necessari per la gestione del "
    "sinistro. Il conferimento è facoltativo ma il rifiuto potrebbe "
    "impedire la gestione della pratica. Base giuridica: art. 9(2)(g) "
    "GDPR — assicurazione e previdenza sociale."
)


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def anonimizza_ip(ip_address: str) -> str:
    """SHA-256 hash of the IP address — never store raw IP (Art. 5 GDPR)."""
    return hashlib.sha256(ip_address.encode("utf-8")).hexdigest()


def calcola_data_scadenza_conservazione(data_completamento: datetime) -> datetime:
    """Return *data_completamento* + 10 years (Art. 2946 C.C.)."""
    return data_completamento.replace(
        year=data_completamento.year + RETENTION_SINISTRI_ANNI
    )


# ---------------------------------------------------------------------------
# Core GDPR functions
# ---------------------------------------------------------------------------


async def registra_consenso(
    db: AsyncSession,
    session_id: str,
    consenso_trattamento: bool,
    consenso_dati_sensibili: bool,
    consenso_registrazione_audio: bool = False,
    consenso_comunicazione_terzi: bool = False,
    ip_hash: Optional[str] = None,
    canale: str = "voce",
) -> ConsensoGDPR:
    """Create a GDPR consent record (Art. 7 — proof of consent).

    Raises ``ValueError`` if *consenso_trattamento* is ``False`` because
    processing cannot proceed without lawful basis (Art. 6(1)(b)).
    """
    if not consenso_trattamento:
        raise ValueError(
            "Il consenso al trattamento dei dati personali è obbligatorio "
            "ai sensi dell'art. 6(1)(b) del GDPR per l'esecuzione del "
            "contratto assicurativo.  Impossibile procedere senza base "
            "giuridica."
        )

    # Link to sinistro if it exists
    sinistro = await get_sinistro_by_session(db, session_id)
    sinistro_id = sinistro.id if sinistro else None

    consenso = ConsensoGDPR(
        id=_uuid(),
        session_id=session_id,
        sinistro_id=sinistro_id,
        ip_hash=ip_hash,
        consenso_trattamento=consenso_trattamento,
        consenso_registrazione_audio=consenso_registrazione_audio,
        consenso_dati_sensibili=consenso_dati_sensibili,
        consenso_comunicazione_terzi=consenso_comunicazione_terzi,
        testo_consenso_versione=CONSENSO_VERSIONE,
        canale=canale,
    )
    db.add(consenso)

    # Audit trail — Art. 5(2) accountability
    audit = AuditLogGDPR(
        id=_uuid(),
        azione="consenso_acquisito",
        risorsa_tipo="consenso",
        risorsa_id=consenso.id,
        dettagli_json={
            "trattamento": consenso_trattamento,
            "dati_sensibili": consenso_dati_sensibili,
            "audio": consenso_registrazione_audio,
            "terzi": consenso_comunicazione_terzi,
            "versione": CONSENSO_VERSIONE,
            "canale": canale,
        },
        esito="successo",
    )
    db.add(audit)
    await db.flush()
    return consenso


async def verifica_consenso(db: AsyncSession, session_id: str) -> dict:
    """Check whether valid consent exists for *session_id*."""
    result = await db.execute(
        select(ConsensoGDPR)
        .where(ConsensoGDPR.session_id == session_id)
        .where(ConsensoGDPR.revocato == False)  # noqa: E712
        .order_by(ConsensoGDPR.timestamp.desc())
        .limit(1)
    )
    consenso = result.scalars().first()

    if consenso is None:
        return {
            "has_consent": False,
            "dati_sensibili": False,
            "audio_consent": False,
            "versione": None,
            "timestamp": None,
        }

    return {
        "has_consent": bool(consenso.consenso_trattamento),
        "dati_sensibili": bool(consenso.consenso_dati_sensibili),
        "audio_consent": bool(consenso.consenso_registrazione_audio),
        "versione": consenso.testo_consenso_versione,
        "timestamp": consenso.timestamp.isoformat() if consenso.timestamp else None,
    }


async def esercita_diritto_cancellazione(
    db: AsyncSession,
    session_id: str,
    richiedente: str,
    motivo: Optional[str] = None,
) -> dict:
    """Implement Art. 17 GDPR Right to Erasure (diritto alla cancellazione).

    If the claim is within the 10-year retention period mandated by
    Art. 2946 C.C. *and* is still active, erasure is denied with a
    legally compliant explanation.

    When erasure is permitted:
    - PII columns are overwritten with ``[CANCELLATO]``
    - claim_data_json PII fields are nulled
    - All transcript rows are deleted
    - dati_cancellati flag is set
    - An immutable audit record is created
    """
    sinistro = await get_sinistro_by_session(db, session_id)
    if sinistro is None:
        raise ValueError(f"Nessun sinistro trovato per session_id={session_id}")

    now = _utcnow()

    # Check legal retention obligation (Art. 2946 C.C.)
    if sinistro.created_at:
        retention_expires = calcola_data_scadenza_conservazione(sinistro.created_at)
        within_retention = now < retention_expires
    else:
        within_retention = True
        retention_expires = None

    # Active claims within retention period cannot be deleted
    active_states = {
        "in_acquisizione", "in_istruttoria", "in_valutazione",
        "perizia_richiesta", "in_liquidazione",
    }
    if within_retention and sinistro.stato in active_states:
        # Log the denied request
        audit = AuditLogGDPR(
            id=_uuid(),
            azione="eliminazione",
            risorsa_tipo="sinistro",
            risorsa_id=sinistro.id,
            dettagli_json={
                "richiedente": richiedente,
                "motivo_richiesta": motivo,
                "retention_expires": retention_expires.isoformat() if retention_expires else None,
            },
            esito="rifiutato",
            nota=(
                "Obbligo di conservazione ai sensi dell'art. 2946 C.C. "
                "— conservazione per 10 anni"
            ),
        )
        db.add(audit)
        await db.flush()

        return {
            "cancellato": False,
            "motivo": (
                "Obbligo di conservazione ai sensi dell'art. 2946 C.C. "
                "— conservazione per 10 anni"
            ),
        }

    # Erasure is permitted — overwrite PII fields
    sinistro.policyholder_name = "[CANCELLATO]"
    sinistro.codice_fiscale = "[CANCELLATO]"
    sinistro.contact_method = "[CANCELLATO]"
    sinistro.targa_veicolo = "[CANCELLATO]"

    # Null PII inside claim_data_json
    if sinistro.claim_data_json and isinstance(sinistro.claim_data_json, dict):
        sanitized = dict(sinistro.claim_data_json)
        for pii_key in [
            "policyholder_name", "codice_fiscale", "contact_method",
            "targa_veicolo", "policy_number",
        ]:
            if pii_key in sanitized:
                sanitized[pii_key] = None
        sinistro.claim_data_json = sanitized

    # Delete all transcript rows
    await db.execute(
        delete(TurnTranscript).where(TurnTranscript.sinistro_id == sinistro.id)
    )

    # Mark as erased
    sinistro.dati_cancellati = True
    sinistro.cancellato_at = now
    sinistro.transcript_json = None

    # Audit log — successful erasure
    audit = AuditLogGDPR(
        id=_uuid(),
        azione="eliminazione",
        risorsa_tipo="sinistro",
        risorsa_id=sinistro.id,
        dettagli_json={
            "richiedente": richiedente,
            "motivo_richiesta": motivo,
            "campi_cancellati": [
                "policyholder_name", "codice_fiscale",
                "contact_method", "targa_veicolo",
                "trascrizioni",
            ],
        },
        esito="successo",
    )
    db.add(audit)
    await db.flush()

    return {
        "cancellato": True,
        "timestamp": now.isoformat(),
    }


async def genera_registro_trattamenti(db: AsyncSession) -> dict:
    """Generate Art. 30 GDPR Record of Processing Activities (ROPA).

    Returns a structured dict representing the processing register
    entry for this FNOL intake system, including live statistics.
    """
    result = await db.execute(select(func.count(Sinistro.id)))
    totale_sinistri = result.scalar() or 0

    return {
        "titolare": "[Nome Compagnia]",
        "finalita": "Gestione sinistri — acquisizione FNOL",
        "base_giuridica": "Art. 6(1)(b) GDPR — esecuzione contratto",
        "categorie_interessati": [
            "assicurati",
            "terzi coinvolti nel sinistro",
            "testimoni",
        ],
        "categorie_dati": [
            "dati anagrafici",
            "dati di contatto",
            "dati relativi a sinistri",
            "dati sulla salute (art. 9)",
        ],
        "destinatari": [
            "periti",
            "liquidatori",
            "riassicuratori",
            "CONSAP",
            "INAIL",
            "autorità giudiziarie",
        ],
        "trasferimenti_extra_ue": (
            "Nessuno — tutti i dati trattati in territorio UE"
        ),
        "misure_sicurezza": [
            "cifratura TLS",
            "autenticazione JWT",
            "controllo accessi RBAC",
            "audit log completo",
        ],
        "periodo_conservazione": (
            f"{RETENTION_SINISTRI_ANNI} anni dal completamento del sinistro"
        ),
        "dpo_contatto": "dpo@compagnia.it",
        "totale_sinistri": totale_sinistri,
        "generato_at": _utcnow().isoformat(),
    }


async def log_accesso_dati_sensibili(
    db: AsyncSession,
    operator_id: str,
    sinistro_id: str,
    azione: str,
    dettagli: Optional[dict] = None,
) -> None:
    """Log access to special-category data (Art. 9 GDPR).

    Every read or write of health/injury data MUST be logged for
    accountability (Art. 5(2) GDPR) and IVASS compliance.
    """
    audit = AuditLogGDPR(
        id=_uuid(),
        operator_id=operator_id,
        azione="accesso_dati_sensibili",
        risorsa_tipo="sinistro",
        risorsa_id=sinistro_id,
        dettagli_json=dettagli or {"azione_dettaglio": azione},
        esito="successo",
    )
    db.add(audit)
    await db.flush()


# ---------------------------------------------------------------------------
# Pydantic schemas for the API layer
# ---------------------------------------------------------------------------


class ConsensoRequest(BaseModel):
    """POST body for /gdpr/consenso."""
    session_id: str = Field(..., description="WebSocket session identifier")
    consenso_trattamento: bool = Field(
        ..., description="Art. 6(1)(b) processing consent"
    )
    consenso_dati_sensibili: bool = Field(
        ..., description="Art. 9 health/injury data consent"
    )
    consenso_registrazione_audio: bool = Field(
        default=False, description="Art. 6(1)(a) voice recording consent"
    )
    consenso_comunicazione_terzi: bool = Field(
        default=False, description="Third-party data sharing consent"
    )


class ConsensoResponse(BaseModel):
    ok: bool
    versione: str
    timestamp: str


class ConsensoStatus(BaseModel):
    has_consent: bool
    dati_sensibili: bool
    audio_consent: bool
    versione: Optional[str] = None
    timestamp: Optional[str] = None


class CancellazioneRequest(BaseModel):
    motivo: Optional[str] = Field(
        default=None, description="Reason for the erasure request"
    )


class CancellazioneResponse(BaseModel):
    cancellato: bool
    motivo: Optional[str] = None
    timestamp: Optional[str] = None


class AuditLogEntry(BaseModel):
    id: str
    timestamp: str
    operator_id: Optional[str] = None
    azione: str
    risorsa_tipo: str
    risorsa_id: str
    dettagli_json: Optional[dict] = None
    esito: str
    nota: Optional[str] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# FastAPI GDPR router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/gdpr", tags=["GDPR"])


@router.post("/consenso", response_model=ConsensoResponse)
async def post_consenso(body: ConsensoRequest) -> ConsensoResponse:
    """Record GDPR consent for a claim session (Art. 7)."""
    try:
        async with get_db() as db:
            consenso = await registra_consenso(
                db,
                session_id=body.session_id,
                consenso_trattamento=body.consenso_trattamento,
                consenso_dati_sensibili=body.consenso_dati_sensibili,
                consenso_registrazione_audio=body.consenso_registrazione_audio,
                consenso_comunicazione_terzi=body.consenso_comunicazione_terzi,
            )
            return ConsensoResponse(
                ok=True,
                versione=consenso.testo_consenso_versione,
                timestamp=consenso.timestamp.isoformat(),
            )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.get("/consenso/{session_id}", response_model=ConsensoStatus)
async def get_consenso(session_id: str) -> ConsensoStatus:
    """Check consent status for a session (claimant can check their own)."""
    async with get_db() as db:
        result = await verifica_consenso(db, session_id)
    return ConsensoStatus(**result)


@router.delete("/cancella/{session_id}", response_model=CancellazioneResponse)
async def delete_data(
    session_id: str,
    body: CancellazioneRequest,
    current_operator: OperatorOut = Depends(get_current_operator),
) -> CancellazioneResponse:
    """Exercise Art. 17 GDPR Right to Erasure (requires operator auth)."""
    async with get_db() as db:
        try:
            result = await esercita_diritto_cancellazione(
                db,
                session_id=session_id,
                richiedente=f"{current_operator.nome} {current_operator.cognome}",
                motivo=body.motivo,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )
    return CancellazioneResponse(**result)


@router.get("/registro-trattamenti")
async def registro_trattamenti(
    current_operator: OperatorOut = Depends(get_current_operator),
) -> dict:
    """Art. 30 GDPR Record of Processing Activities (admin only)."""
    if current_operator.ruolo not in ("admin", "supervisore"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli amministratori possono accedere al registro dei trattamenti.",
        )
    async with get_db() as db:
        return await genera_registro_trattamenti(db)


@router.get("/audit-log", response_model=List[AuditLogEntry])
async def audit_log(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    risorsa_id: Optional[str] = Query(None),
    current_operator: OperatorOut = Depends(get_current_operator),
) -> List[AuditLogEntry]:
    """Retrieve GDPR audit log entries (admin only)."""
    if current_operator.ruolo not in ("admin", "supervisore"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli amministratori possono accedere all'audit log.",
        )
    async with get_db() as db:
        stmt = select(AuditLogGDPR).order_by(AuditLogGDPR.timestamp.desc())
        if risorsa_id:
            stmt = stmt.where(AuditLogGDPR.risorsa_id == risorsa_id)
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        rows = result.scalars().all()
    return [
        AuditLogEntry(
            id=r.id,
            timestamp=r.timestamp.isoformat() if r.timestamp else "",
            operator_id=r.operator_id,
            azione=r.azione,
            risorsa_tipo=r.risorsa_tipo,
            risorsa_id=r.risorsa_id,
            dettagli_json=r.dettagli_json,
            esito=r.esito,
            nota=r.nota,
        )
        for r in rows
    ]
