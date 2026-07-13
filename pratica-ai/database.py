"""SQLAlchemy 2.x async database layer for the Italian FNOL voice agent.

Provides persistent storage for claim sessions (sinistri), operator
accounts, and turn-level transcripts.  Uses aiosqlite for local
development; swap DATABASE_URL for any async-compatible engine in
production (e.g. asyncpg for PostgreSQL).
"""

from __future__ import annotations

import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeBase, relationship

# ---------------------------------------------------------------------------
# Engine configuration
# ---------------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./pratica_ai_db.db")

# === FIX 4: Connection pooling for production scale ===
_is_sqlite = "sqlite" in DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # 20 persistent connections
    max_overflow=40,        # 40 additional on demand
    pool_timeout=30,        # wait max 30s for connection
    pool_recycle=1800,      # recycle connections every 30min
    pool_pre_ping=True,     # test connection before use
    echo=False,             # no SQL logging in production
    # SQLite needs this for concurrent writes
    connect_args={"check_same_thread": False} if _is_sqlite else {},
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class Operator(Base):
    """Insurance operator / agent account (operatori)."""

    __tablename__ = "operatori"

    id = Column(String(36), primary_key=True, default=_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    nome = Column(String(128), nullable=False)
    cognome = Column(String(128), nullable=False)
    ruolo = Column(
        String(32),
        nullable=False,
        default="operatore",
        comment="operatore | liquidatore | supervisore | admin",
    )
    attivo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # relationship
    sinistri = relationship("Sinistro", back_populates="operator", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Operator {self.email} ({self.ruolo})>"


class Sinistro(Base):
    """Insurance claim record (sinistri)."""

    __tablename__ = "sinistri"

    id = Column(String(36), primary_key=True, default=_uuid)
    session_id = Column(String(128), unique=True, index=True, nullable=False)
    operator_id = Column(
        String(36), ForeignKey("operatori.id"), nullable=True
    )

    # Status
    stato = Column(
        String(32),
        nullable=False,
        default="in_acquisizione",
        comment="ItalianClaimStatus values",
    )
    claim_type = Column(String(64), nullable=True)

    # Policyholder
    policyholder_name = Column(String(255), nullable=True)
    codice_fiscale = Column(String(16), nullable=True)
    contact_method = Column(String(255), nullable=True)
    policy_number = Column(String(128), nullable=True)

    # Loss details
    date_of_loss = Column(String(128), nullable=True)
    loss_location = Column(String(512), nullable=True)
    targa_veicolo = Column(String(16), nullable=True)
    provincia = Column(String(2), nullable=True)
    estimated_loss_eur = Column(Float, nullable=True)

    # JSON blobs for full data
    claim_data_json = Column(JSON, nullable=True)
    intake_packet_json = Column(JSON, nullable=True)
    transcript_json = Column(JSON, nullable=True)

    # CARD / CONSAP / SIU flags
    card_eligible = Column(Boolean, nullable=True)
    consap_routing = Column(Boolean, nullable=True)
    siu_flagged = Column(Boolean, nullable=True)
    siu_signals_json = Column(JSON, nullable=True)

    # GDPR — Art. 17 erasure tracking & retention management
    dati_cancellati = Column(Boolean, default=False, nullable=False)
    cancellato_at = Column(DateTime(timezone=True), nullable=True)
    motivo_conservazione = Column(
        String(512),
        nullable=True,
        comment="Legal basis for retention beyond standard period",
    )
    retention_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    operator = relationship("Operator", back_populates="sinistri", lazy="selectin")
    trascrizioni = relationship(
        "TurnTranscript", back_populates="sinistro", lazy="selectin",
        order_by="TurnTranscript.turno_numero",
    )

    def __repr__(self) -> str:
        return f"<Sinistro {self.session_id} [{self.stato}]>"


class TurnTranscript(Base):
    """Single transcript turn (trascrizioni)."""

    __tablename__ = "trascrizioni"

    id = Column(String(36), primary_key=True, default=_uuid)
    sinistro_id = Column(
        String(36), ForeignKey("sinistri.id"), nullable=False, index=True
    )
    ruolo = Column(
        String(32),
        nullable=False,
        comment="assicurato | agente",
    )
    testo = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    turno_numero = Column(Integer, nullable=False, default=0)

    # Relationship
    sinistro = relationship("Sinistro", back_populates="trascrizioni")

    def __repr__(self) -> str:
        return f"<TurnTranscript #{self.turno_numero} [{self.ruolo}]>"


class ConsensoGDPR(Base):
    """GDPR consent record (consensi_gdpr).

    Tracks explicit consent per Art. 6, 7, and 9 GDPR.
    Each consent action produces a new immutable row so the full
    consent lifecycle can be audited.
    """

    __tablename__ = "consensi_gdpr"

    id = Column(String(36), primary_key=True, default=_uuid)
    session_id = Column(String(128), index=True, nullable=False)
    sinistro_id = Column(
        String(36), ForeignKey("sinistri.id"), nullable=True
    )
    timestamp = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    ip_hash = Column(
        String(64),
        nullable=True,
        comment="SHA-256 of IP — raw IP is never stored",
    )

    # Consent flags
    consenso_trattamento = Column(
        Boolean, nullable=False,
        comment="Art. 6(1)(b) processing consent",
    )
    consenso_registrazione_audio = Column(
        Boolean, default=False, nullable=False,
        comment="Art. 6(1)(a) explicit consent for voice recording",
    )
    consenso_dati_sensibili = Column(
        Boolean, default=False, nullable=False,
        comment="Art. 9 explicit consent for health/injury data",
    )
    consenso_comunicazione_terzi = Column(
        Boolean, default=False, nullable=False,
        comment="Consent for data sharing with third parties",
    )

    testo_consenso_versione = Column(
        String(32), nullable=False,
        comment="Version of consent text shown to the data subject",
    )
    revocato = Column(Boolean, default=False, nullable=False)
    revocato_at = Column(DateTime(timezone=True), nullable=True)
    canale = Column(
        String(16), nullable=False, default="voce",
        comment="voce | testo | web",
    )

    def __repr__(self) -> str:
        return (
            f"<ConsensoGDPR {self.session_id} "
            f"trattamento={self.consenso_trattamento} "
            f"v{self.testo_consenso_versione}>"
        )


class AuditLogGDPR(Base):
    """GDPR audit log (audit_log_gdpr).

    Immutable log of every action on personal data for Art. 30 GDPR
    record-of-processing and Art. 5(2) accountability.
    """

    __tablename__ = "audit_log_gdpr"

    id = Column(String(36), primary_key=True, default=_uuid)
    timestamp = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    operator_id = Column(
        String(36), ForeignKey("operatori.id"), nullable=True
    )
    azione = Column(
        String(64), nullable=False,
        comment=(
            "visualizzazione | modifica | esportazione | eliminazione | "
            "consenso_acquisito | accesso_dati_sensibili | trasmissione_terzi"
        ),
    )
    risorsa_tipo = Column(
        String(32), nullable=False,
        comment="sinistro | trascrizione | consenso",
    )
    risorsa_id = Column(String(36), nullable=False)
    dettagli_json = Column(JSON, nullable=True)
    esito = Column(
        String(16), nullable=False, default="successo",
        comment="successo | rifiutato",
    )
    nota = Column(String(512), nullable=True)

    def __repr__(self) -> str:
        return f"<AuditLogGDPR {self.azione} {self.risorsa_tipo}:{self.risorsa_id}>"


# ---------------------------------------------------------------------------
# Database lifecycle
# ---------------------------------------------------------------------------


async def init_db() -> None:
    """Create all tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager that yields a database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# CRUD — Sinistro
# ---------------------------------------------------------------------------


async def create_sinistro(
    db: AsyncSession,
    session_id: str,
    operator_id: Optional[str] = None,
) -> Sinistro:
    """Create a new claim record bound to a WebSocket session."""
    sinistro = Sinistro(
        id=_uuid(),
        session_id=session_id,
        operator_id=operator_id,
        stato="in_acquisizione",
    )
    db.add(sinistro)
    await db.flush()
    return sinistro


async def get_sinistro_by_session(
    db: AsyncSession, session_id: str
) -> Optional[Sinistro]:
    """Retrieve a claim by its WebSocket session ID."""
    result = await db.execute(
        select(Sinistro).where(Sinistro.session_id == session_id)
    )
    return result.scalars().first()


async def update_sinistro_claim_data(
    db: AsyncSession,
    session_id: str,
    claim_data: dict | None = None,
    intake_packet: dict | None = None,
    stato: str | None = None,
) -> Optional[Sinistro]:
    """Update structured claim data on an existing sinistro record."""
    sinistro = await get_sinistro_by_session(db, session_id)
    if sinistro is None:
        return None

    if claim_data is not None:
        sinistro.claim_data_json = claim_data
        # Denormalize frequently-queried fields
        sinistro.policyholder_name = claim_data.get("policyholder_name")
        sinistro.codice_fiscale = claim_data.get("codice_fiscale")
        sinistro.contact_method = claim_data.get("contact_method")
        sinistro.policy_number = claim_data.get("policy_number")
        sinistro.date_of_loss = claim_data.get("date_of_loss")
        sinistro.loss_location = claim_data.get("loss_location")
        sinistro.targa_veicolo = claim_data.get("targa_veicolo")
        sinistro.provincia = claim_data.get("provincia")
        sinistro.estimated_loss_eur = claim_data.get("estimated_loss_eur")

    if intake_packet is not None:
        sinistro.intake_packet_json = intake_packet
        sinistro.claim_type = intake_packet.get("claim_type")
        sinistro.siu_flagged = bool(intake_packet.get("fraud_safety_signals"))
        if intake_packet.get("fraud_safety_signals"):
            sinistro.siu_signals_json = [
                s if isinstance(s, dict) else s
                for s in intake_packet["fraud_safety_signals"]
            ]

    if stato is not None:
        sinistro.stato = stato
        if stato == "definito":
            sinistro.completed_at = _utcnow()

    sinistro.updated_at = _utcnow()
    await db.flush()
    return sinistro


async def add_transcript_turn(
    db: AsyncSession,
    sinistro_id: str,
    ruolo: str,
    testo: str,
) -> TurnTranscript:
    """Append a transcript turn to a sinistro."""
    # Determine next turn number
    result = await db.execute(
        select(TurnTranscript)
        .where(TurnTranscript.sinistro_id == sinistro_id)
        .order_by(TurnTranscript.turno_numero.desc())
        .limit(1)
    )
    last = result.scalars().first()
    next_num = (last.turno_numero + 1) if last else 1

    turn = TurnTranscript(
        id=_uuid(),
        sinistro_id=sinistro_id,
        ruolo=ruolo,
        testo=testo,
        turno_numero=next_num,
    )
    db.add(turn)
    await db.flush()
    return turn


async def get_all_sinistri(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
) -> List[Sinistro]:
    """List claim records with pagination."""
    result = await db.execute(
        select(Sinistro)
        .order_by(Sinistro.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# CRUD — Operator
# ---------------------------------------------------------------------------


async def create_operator(
    db: AsyncSession,
    email: str,
    hashed_password: str,
    nome: str,
    cognome: str,
    ruolo: str = "operatore",
) -> Operator:
    """Create a new operator account."""
    operator = Operator(
        id=_uuid(),
        email=email.lower().strip(),
        hashed_password=hashed_password,
        nome=nome,
        cognome=cognome,
        ruolo=ruolo,
    )
    db.add(operator)
    await db.flush()
    return operator


async def get_operator_by_email(
    db: AsyncSession, email: str
) -> Optional[Operator]:
    """Retrieve an operator by email address."""
    result = await db.execute(
        select(Operator).where(Operator.email == email.lower().strip())
    )
    return result.scalars().first()
