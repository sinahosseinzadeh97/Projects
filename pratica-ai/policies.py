"""Deterministic policy, evidence, routing, and packet builders — Italian market.

Implements Italian insurance regulations including:
- CARD (Convenzione tra Assicuratori per il Risarcimento Diretto)
- CONSAP (Fondo di Garanzia Vittime della Strada)
- Art. 1913 C.C. notification deadlines
- Art. 1915 C.C. forfeiture risk for late reporting
- IVASS circulars and D.Lgs. 209/2005 (Codice delle Assicurazioni Private)
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any

try:
    from .schemas import (
        ClaimClassification,
        ClaimIntakePacket,
        ClaimNarrative,
        CoverageEvidenceDecision,
        DocumentChecklist,
        DocumentChecklistItem,
        EvidenceRuleFinding,
        FieldValidation,
        FraudSafetyGate,
        FraudSafetySignal,
        ItalianClaimStatus,
        ItalianDocumentType,
    )
except ImportError:
    from schemas import (
        ClaimClassification,
        ClaimIntakePacket,
        ClaimNarrative,
        CoverageEvidenceDecision,
        DocumentChecklist,
        DocumentChecklistItem,
        EvidenceRuleFinding,
        FieldValidation,
        FraudSafetyGate,
        FraudSafetySignal,
        ItalianClaimStatus,
        ItalianDocumentType,
    )


# ---------------------------------------------------------------------------
# SECTION 1: Required documents per Italian claim type
# Each entry: (ItalianDocumentType value, Italian description, condition tag)
# Condition tags: "always", "police", "injury", "repair", "criminal",
#   "workplace", "serious", "third_party", "theft", "recommended", "weather",
#   "medical", "cancellation", "baggage"
# ---------------------------------------------------------------------------

TYPE_REQUIRED_DOCS: dict[str, list[tuple[str, str, str]]] = {
    "rc_auto": [
        (ItalianDocumentType.denuncia_di_sinistro.value,
         "Obbligatoria per l'apertura della pratica sinistri.", "always"),
        (ItalianDocumentType.modulo_cai_cid.value,
         "Constatazione Amichevole di Incidente — fondamentale per la determinazione della responsabilità.", "always"),
        (ItalianDocumentType.foto_danni.value,
         "Documentazione fotografica dei danni ai veicoli e alla scena.", "always"),
        (ItalianDocumentType.verbale_polizia.value,
         "Verbale della Polizia Stradale, se intervenuta.", "police"),
        (ItalianDocumentType.verbale_carabinieri.value,
         "Verbale dei Carabinieri, se intervenuti.", "police"),
        (ItalianDocumentType.referto_medico.value,
         "Referto del Pronto Soccorso in caso di lesioni personali.", "injury"),
        (ItalianDocumentType.fattura_riparazione.value,
         "Fattura della carrozzeria autorizzata per la riparazione.", "repair"),
        (ItalianDocumentType.preventivo_riparazione.value,
         "Preventivo di riparazione del veicolo danneggiato.", "repair"),
    ],
    "kasko": [
        (ItalianDocumentType.denuncia_di_sinistro.value,
         "Obbligatoria per attivare la copertura Kasko.", "always"),
        (ItalianDocumentType.foto_danni.value,
         "Documentazione fotografica dei danni al veicolo.", "always"),
        (ItalianDocumentType.fattura_riparazione.value,
         "Fattura di riparazione del veicolo.", "repair"),
        (ItalianDocumentType.preventivo_riparazione.value,
         "Preventivo di riparazione del veicolo.", "repair"),
        (ItalianDocumentType.verbale_polizia.value,
         "Verbale delle autorità, se coinvolti terzi.", "third_party"),
    ],
    "furto_veicolo": [
        (ItalianDocumentType.denuncia_furto.value,
         "Denuncia alle autorità competenti — obbligatoria per legge in caso di furto.", "always"),
        (ItalianDocumentType.denuncia_di_sinistro.value,
         "Denuncia di sinistro alla compagnia assicuratrice.", "always"),
        (ItalianDocumentType.foto_danni.value,
         "Foto dei danni in caso di furto parziale o tentato furto.", "recommended"),
    ],
    "incendio": [
        (ItalianDocumentType.denuncia_di_sinistro.value,
         "Obbligatoria per la denuncia dell'incendio alla compagnia.", "always"),
        ("verbale_vigili_del_fuoco",
         "Verbale dei Vigili del Fuoco — necessario per accertare causa e dinamica.", "always"),
        (ItalianDocumentType.foto_danni.value,
         "Documentazione fotografica dei danni causati dall'incendio.", "always"),
        (ItalianDocumentType.verbale_polizia.value,
         "Verbale delle autorità in caso di sospetto incendio doloso.", "criminal"),
        (ItalianDocumentType.preventivo_riparazione.value,
         "Preventivo di ripristino dei beni danneggiati.", "repair"),
        (ItalianDocumentType.fattura_riparazione.value,
         "Fattura per i lavori di ripristino eseguiti.", "repair"),
    ],
    "furto_casa": [
        (ItalianDocumentType.denuncia_furto.value,
         "Denuncia di furto alle autorità — obbligatoria per legge.", "always"),
        (ItalianDocumentType.denuncia_di_sinistro.value,
         "Denuncia di sinistro alla compagnia assicuratrice.", "always"),
        (ItalianDocumentType.foto_danni.value,
         "Documentazione fotografica dei danni e dei segni di effrazione.", "always"),
        ("elenco_beni_sottratti",
         "Elenco dettagliato dei beni sottratti con valori stimati.", "recommended"),
    ],
    "acqua_condotta": [
        (ItalianDocumentType.denuncia_di_sinistro.value,
         "Obbligatoria per i danni da acqua condotta.", "always"),
        (ItalianDocumentType.foto_danni.value,
         "Documentazione fotografica dei danni da allagamento.", "always"),
        (ItalianDocumentType.preventivo_riparazione.value,
         "Preventivo per il ripristino delle aree danneggiate.", "repair"),
        ("verbale_condominio",
         "Verbale dell'assemblea condominiale se il danno coinvolge terzi.", "third_party"),
    ],
    "infortuni": [
        (ItalianDocumentType.denuncia_di_sinistro.value,
         "Obbligatoria per la denuncia dell'infortunio.", "always"),
        (ItalianDocumentType.referto_medico.value,
         "Referto medico del Pronto Soccorso o del medico curante.", "always"),
        ("verbale_inail",
         "Denuncia INAIL in caso di infortunio sul lavoro.", "workplace"),
        ("certificato_medico_specialistico",
         "Certificato medico specialistico per infortuni gravi o con postumi.", "serious"),
    ],
    "rc_generale": [
        (ItalianDocumentType.denuncia_di_sinistro.value,
         "Obbligatoria per l'apertura della pratica RC.", "always"),
        (ItalianDocumentType.atto_di_citazione.value,
         "Atto di citazione o richiesta risarcitoria del terzo danneggiato.", "third_party"),
        ("lettera_di_messa_in_mora",
         "Lettera di messa in mora del terzo danneggiato.", "third_party"),
        (ItalianDocumentType.foto_danni.value,
         "Documentazione fotografica a supporto del danno.", "recommended"),
    ],
    "tutela_legale": [
        (ItalianDocumentType.denuncia_di_sinistro.value,
         "Obbligatoria per l'attivazione della copertura legale.", "always"),
        (ItalianDocumentType.atto_di_citazione.value,
         "Atto di citazione o provvedimento giudiziario.", "always"),
        ("documentazione_legale",
         "Documentazione legale a supporto della vertenza.", "recommended"),
    ],
    "cristalli": [
        (ItalianDocumentType.denuncia_di_sinistro.value,
         "Obbligatoria per la copertura cristalli.", "always"),
        (ItalianDocumentType.foto_danni.value,
         "Foto del cristallo danneggiato o rotto.", "always"),
        (ItalianDocumentType.fattura_riparazione.value,
         "Fattura della sostituzione/riparazione da carrozzeria autorizzata.", "repair"),
    ],
    "grandine": [
        (ItalianDocumentType.denuncia_di_sinistro.value,
         "Obbligatoria per la denuncia danni da grandine.", "always"),
        (ItalianDocumentType.foto_danni.value,
         "Documentazione fotografica dei danni da grandine.", "always"),
        ("bollettino_meteorologico",
         "Bollettino meteorologico a comprova dell'evento atmosferico.", "weather"),
        (ItalianDocumentType.preventivo_riparazione.value,
         "Preventivo di riparazione del veicolo/bene.", "repair"),
        (ItalianDocumentType.fattura_riparazione.value,
         "Fattura della riparazione effettuata.", "repair"),
    ],
    "viaggio": [
        (ItalianDocumentType.denuncia_di_sinistro.value,
         "Obbligatoria per l'attivazione della copertura viaggio.", "always"),
        (ItalianDocumentType.referto_medico.value,
         "Referto medico per spese sanitarie sostenute all'estero.", "medical"),
        ("ricevute_spese_mediche",
         "Ricevute e fatture delle spese mediche sostenute.", "medical"),
        ("documentazione_cancellazione",
         "Documentazione comprovante l'annullamento del viaggio.", "cancellation"),
        (ItalianDocumentType.denuncia_furto.value,
         "Denuncia alle autorità locali in caso di furto bagagli.", "baggage"),
    ],
    "other": [
        (ItalianDocumentType.denuncia_di_sinistro.value,
         "Denuncia di sinistro alla compagnia assicuratrice.", "always"),
        (ItalianDocumentType.foto_danni.value,
         "Documentazione fotografica dell'evento.", "recommended"),
        (ItalianDocumentType.preventivo_riparazione.value,
         "Preventivo o fattura a supporto del danno.", "recommended"),
    ],
}


# ---------------------------------------------------------------------------
# SECTION 2: Italian timing rules (Art. 1913 C.C.)
# ---------------------------------------------------------------------------

# Notification deadlines in calendar days per claim type
ITALIAN_REPORTING_DEADLINES: dict[str, int] = {
    "rc_auto": 3,
    "furto_veicolo": 2,
    "furto_casa": 3,
    "acqua_condotta": 3,
    "incendio": 3,
    "kasko": 5,
    "infortuni": 5,
    "rc_generale": 5,
    "tutela_legale": 10,
    "cristalli": 5,
    "grandine": 5,
    "viaggio": 5,
}

DEFAULT_REPORTING_DEADLINE_DAYS: int = 5


def check_reporting_timeliness(
    claim_type: str,
    date_of_loss: datetime | None,
    reported_date: datetime | None,
) -> dict[str, Any]:
    """Evaluate whether the claim was reported within Italian legal deadlines.

    Returns a dict with:
      - timeliness_status: "on_time" | "late_warning" | "late_critical" | "unknown"
      - deadline_days: int
      - actual_days: int | None
      - legal_reference: str
      - message: str (Italian)
    """
    deadline = ITALIAN_REPORTING_DEADLINES.get(claim_type, DEFAULT_REPORTING_DEADLINE_DAYS)

    if date_of_loss is None or reported_date is None:
        return {
            "timeliness_status": "unknown",
            "deadline_days": deadline,
            "actual_days": None,
            "legal_reference": "Art. 1913 C.C. — Obbligo di avviso",
            "message": "Impossibile verificare la tempestività: date mancanti.",
        }

    delta_days = (reported_date - date_of_loss).days

    if delta_days <= deadline:
        status = "on_time"
        message = (
            f"Sinistro denunciato entro il termine di {deadline} giorni "
            f"previsto dall'Art. 1913 C.C. ({delta_days} giorni effettivi)."
        )
    elif delta_days <= deadline * 2:
        status = "late_warning"
        message = (
            f"Attenzione: denuncia tardiva ({delta_days} giorni, termine previsto: {deadline} giorni). "
            f"La pratica viene comunque acquisita, ma si segnala il ritardo. "
            f"Riferimento: Art. 1913 C.C."
        )
    else:
        status = "late_critical"
        message = (
            f"CRITICO: denuncia molto tardiva ({delta_days} giorni, termine previsto: {deadline} giorni). "
            f"Rischio decadenza ex Art. 1915 C.C. — richiesta supervisione del liquidatore. "
            f"Potrebbe incidere sulla copertura assicurativa."
        )

    return {
        "timeliness_status": status,
        "deadline_days": deadline,
        "actual_days": delta_days,
        "legal_reference": "Art. 1913 C.C. — Obbligo di avviso",
        "message": message,
    }


# ---------------------------------------------------------------------------
# SECTION 3: CARD system (Risarcimento Diretto — D.Lgs. 209/2005 Art. 149-150)
# ---------------------------------------------------------------------------

CARD_DAMAGE_LIMIT_EUR: float = 500_000.0


def check_card_eligibility(claim_data: dict[str, Any]) -> dict[str, Any]:
    """Check eligibility for CARD (Convenzione tra Assicuratori per il Risarcimento Diretto).

    CARD applies when ALL conditions are met:
    1. Claim type is rc_auto
    2. Both vehicles are insured in Italy
    3. Only material damage (no physical injuries beyond micropermanenti)
    4. Claimant was NOT at fault (or partially at fault)
    5. Estimated damage under €500,000
    """
    claim_type = claim_data.get("claim_type", "")
    both_insured_italy = claim_data.get("both_vehicles_insured_italy", False)
    injuries = claim_data.get("injuries_or_safety_concerns", [])
    has_serious_injuries = claim_data.get("has_serious_injuries", False)
    estimated_loss = claim_data.get("estimated_loss_eur") or 0.0
    claimant_at_fault_exclusive = claim_data.get("claimant_at_fault_exclusive", False)

    # Determine if injuries are beyond micropermanenti
    injury_text = " ".join(injuries).lower() if injuries else ""
    has_any_injury = bool(injuries) and _has_any(injury_text, [
        r"\blesion[ei]\b", r"\bfrattur[ae]\b", r"\bricovero\b",
        r"\bintervento chirurgico\b", r"\binvalidità\b",
        r"\bmorte\b", r"\bdecesso\b",
    ])

    reasons: list[str] = []

    if claim_type != "rc_auto":
        reasons.append("Il tipo di sinistro non è RC Auto.")

    if not both_insured_italy:
        reasons.append("Entrambi i veicoli devono essere assicurati in Italia.")

    if has_serious_injuries or has_any_injury:
        reasons.append(
            "Sono presenti lesioni personali gravi (oltre le micropermanenti). "
            "Si applica la procedura ordinaria ex Art. 148 C.d.A."
        )

    if claimant_at_fault_exclusive:
        reasons.append("Il richiedente risulta responsabile esclusivo del sinistro.")

    if estimated_loss > CARD_DAMAGE_LIMIT_EUR:
        reasons.append(
            f"L'importo stimato ({estimated_loss:,.2f} €) supera il limite CARD "
            f"di {CARD_DAMAGE_LIMIT_EUR:,.2f} €."
        )

    if not reasons:
        return {
            "eligible": True,
            "routing": "card_gestionario",
            "next_step": "La liquidiamo direttamente noi tramite procedura di Risarcimento Diretto (CARD).",
            "legal_reference": "D.Lgs. 209/2005, Artt. 149-150 — Risarcimento Diretto",
            "reasons": [],
        }
    else:
        return {
            "eligible": False,
            "routing": "rc_terzi_tradizionale",
            "next_step": "Sinistro gestito con procedura ordinaria (Art. 148 C.d.A.).",
            "legal_reference": "D.Lgs. 209/2005, Art. 148 — Procedura ordinaria",
            "reasons": reasons,
        }


# ---------------------------------------------------------------------------
# SECTION 4: CONSAP routing (Fondo di Garanzia Vittime della Strada)
# ---------------------------------------------------------------------------

def check_consap_routing(claim_data: dict[str, Any]) -> dict[str, Any]:
    """Check if claim should be routed to CONSAP for the Fondo di Garanzia.

    Routes to CONSAP when:
    - rc_auto claim AND
    - At-fault vehicle UNINSURED, or
    - At-fault driver FLED (pirateria della strada), or
    - Vehicle plates STOLEN or CLONED
    """
    claim_type = claim_data.get("claim_type", "")
    at_fault_uninsured = claim_data.get("at_fault_vehicle_uninsured", False)
    at_fault_fled = claim_data.get("at_fault_driver_fled", False)
    plates_stolen_cloned = claim_data.get("plates_stolen_or_cloned", False)

    if claim_type != "rc_auto":
        return {
            "route_to_consap": False,
            "reason": "Non applicabile — il sinistro non è RC Auto.",
            "consap_phone": "800.093.272",
            "consap_website": "www.consap.it",
        }

    if at_fault_uninsured:
        return {
            "route_to_consap": True,
            "reason": "veicolo non assicurato",
            "consap_phone": "800.093.272",
            "consap_website": "www.consap.it",
            "note": (
                "Il veicolo responsabile risulta privo di copertura assicurativa. "
                "La pratica viene instradata al Fondo di Garanzia Vittime della Strada "
                "gestito da CONSAP (D.Lgs. 209/2005, Artt. 283-284)."
            ),
        }

    if at_fault_fled:
        return {
            "route_to_consap": True,
            "reason": "pirateria della strada",
            "consap_phone": "800.093.272",
            "consap_website": "www.consap.it",
            "note": (
                "Il conducente responsabile si è dato alla fuga (pirata della strada). "
                "Necessaria denuncia alle autorità e instradamento al Fondo di Garanzia "
                "gestito da CONSAP."
            ),
        }

    if plates_stolen_cloned:
        return {
            "route_to_consap": True,
            "reason": "targa clonata o rubata",
            "consap_phone": "800.093.272",
            "consap_website": "www.consap.it",
            "note": (
                "La targa del veicolo responsabile risulta rubata o clonata. "
                "La pratica viene instradata al Fondo di Garanzia gestito da CONSAP."
            ),
        }

    return {
        "route_to_consap": False,
        "reason": "Nessuna condizione CONSAP rilevata.",
        "consap_phone": "800.093.272",
        "consap_website": "www.consap.it",
    }


# ---------------------------------------------------------------------------
# Blocking field questions — Italian
# ---------------------------------------------------------------------------

BLOCKING_FIELD_QUESTIONS: dict[str, str] = {
    "policyholder_name": "Qual è il Suo nome e cognome come risulta sulla polizza?",
    "policy_number": "Qual è il numero di polizza, se lo ha a disposizione?",
    "contact_method": "Qual è il recapito telefonico o l'indirizzo e-mail per essere contattato/a dal liquidatore?",
    "date_of_loss": "Quando si è verificato il sinistro?",
    "loss_location": "Dove si è verificato il sinistro?",
    "loss_description": "Può descrivere brevemente l'accaduto?",
}


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _as_model(model_type, value):
    if isinstance(value, model_type):
        return value
    if value is None:
        return model_type()
    if isinstance(value, str):
        return model_type.model_validate_json(value)
    return model_type.model_validate(value)


def _blank(value: Any) -> bool:
    text = str(value or "").strip().lower()
    return text in {"", "unknown", "not specified", "unspecified", "n/a", "none",
                    "not provided", "non specificato", "sconosciuto", "non fornito"}


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = item.strip()
        key = normalized.lower()
        if normalized and key not in seen:
            seen.add(key)
            result.append(normalized)
    return result


def _all_evidence_text(claim: ClaimNarrative) -> str:
    fields = [
        claim.loss_description,
        claim.raw_narrative_summary,
        " ".join(claim.evidence_available),
        " ".join(claim.documents_mentioned),
    ]
    return "\n".join(fields).lower()


def _has_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _without_negated_safety_mentions(text: str) -> str:
    """Remove phrases like 'nessun ferito' before positive safety regex checks."""
    negated_patterns = [
        # English negation patterns (preserved for bilingual transcripts)
        r"\b(?:no|not|none|without|denies|denied)\s+(?:one\s+)?(?:was\s+)?(?:injur\w*|hurt|pain|medical attention|ambulance|hospital|unsafe|hazard\w*|danger)\b",
        # Italian negation patterns
        r"\b(?:nessun[oa]?|senza|non)\s+(?:ferit[oia]?|lesion[ei]|danno fisico|ambulanza|ospedale|ricovero|pericolo)\b",
    ]
    cleaned = text
    for pattern in negated_patterns:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
    return cleaned


def _positive_safety_concerns(claim: ClaimNarrative) -> list[str]:
    return [item for item in claim.injuries_or_safety_concerns if _has_positive_safety_language(item)]


def _has_positive_safety_language(text: str) -> bool:
    cleaned = _without_negated_safety_mentions(text)
    return _has_any(
        cleaned,
        [
            # Italian safety terms
            r"\bferit[oia]\b", r"\blesion[ei]\b", r"\bricovero\b",
            r"\bospedale\b", r"\bambulanza\b", r"\bpronto soccorso\b",
            r"\bcervicalgia\b", r"\blombalgia\b", r"\bcolpo di frusta\b",
            r"\bfrattur[ae]\b", r"\bcontusion[ei]\b",
            # English fallback
            r"\binjur", r"\bhurt\b", r"\bhospital\b", r"\burgent care\b",
            r"\bambulance\b",
        ],
    )


def _document_provided(document: str, claim: ClaimNarrative) -> bool:
    """Check if a document appears to be mentioned in the claim evidence."""
    evidence = _all_evidence_text(claim)
    doc = document.lower()
    # Italian document keyword groups
    keyword_groups = [
        ["foto", "fotografia", "immagin", "video", "photo", "picture"],
        ["polizia", "carabinieri", "verbale", "police", "report"],
        ["fattura", "ricevuta", "scontrino", "receipt", "invoice"],
        ["preventivo", "perizia", "stima", "estimate"],
        ["medico", "referto", "pronto soccorso", "ospedale", "medical", "hospital"],
        ["denuncia", "querela", "esposto"],
        ["cai", "cid", "constatazione amichevole"],
        ["vigili del fuoco", "pompieri"],
        ["inail"],
        ["atto di citazione", "citazione", "messa in mora"],
        ["bollettino meteorologico", "meteo"],
        ["condominio", "assemblea"],
    ]
    for keywords in keyword_groups:
        if any(keyword in doc for keyword in keywords):
            return any(keyword in evidence for keyword in keywords)
    return any(word in evidence for word in doc.split()[:3])


def _parse_date(value: str) -> datetime | None:
    """Parse date strings in multiple formats including Italian DD/MM/YYYY."""
    text = str(value or "").strip()
    if not text:
        return None

    cleaned = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", text, flags=re.IGNORECASE)
    candidates = [cleaned[:10], cleaned]
    formats = [
        "%d/%m/%Y",    # Italian standard: DD/MM/YYYY
        "%d-%m-%Y",    # DD-MM-YYYY
        "%d.%m.%Y",    # DD.MM.YYYY
        "%Y-%m-%d",    # ISO format
        "%m/%d/%Y",    # US format fallback
        "%B %d, %Y",
        "%b %d, %Y",
        "%B %d %Y",
        "%b %d %Y",
    ]
    for candidate in candidates:
        for fmt in formats:
            try:
                return datetime.strptime(candidate, fmt)
            except ValueError:
                continue
    return None


def _format_italian_datetime(dt: datetime | None) -> str:
    """Format a datetime as DD/MM/YYYY HH:MM."""
    if dt is None:
        return "non disponibile"
    return dt.strftime("%d/%m/%Y %H:%M")


def _format_italian_date(dt: datetime | None) -> str:
    """Format a datetime as DD/MM/YYYY."""
    if dt is None:
        return "non disponibile"
    return dt.strftime("%d/%m/%Y")


# ---------------------------------------------------------------------------
# Claimant-facing next message — Italian
# ---------------------------------------------------------------------------

def _next_claimant_message(
    route: str,
    missing: list[str],
    required_documents: list[str],
) -> str:
    if route == "emergency_escalation":
        return (
            "Il Suo sinistro riporta lesioni personali o problematiche di sicurezza. "
            "Un operatore esaminerà immediatamente la Sua pratica. "
            "Se qualcuno è in pericolo, contatti subito il 112 (Numero Unico Emergenze)."
        )

    for field_name in missing:
        if field_name in BLOCKING_FIELD_QUESTIONS:
            return BLOCKING_FIELD_QUESTIONS[field_name]

    if missing:
        return (
            f"Per completare la pratica, potrebbe fornire questo dato mancante: {missing[0]}?"
        )

    if required_documents:
        return (
            f"Ha a disposizione questo documento: {required_documents[0]}? "
            "Lo invii appena possibile per accelerare la liquidazione."
        )

    if route == "special_investigation":
        return (
            "La Sua pratica è stata acquisita e verrà esaminata da un operatore specializzato. "
            "La preghiamo di conservare gli originali di ricevute, foto, referti e ogni altra "
            "documentazione relativa al sinistro."
        )

    return (
        "La Sua pratica contiene le informazioni necessarie per l'assegnazione al liquidatore. "
        "Conservi copia di tutti i documenti, le ricevute, le foto e le comunicazioni "
        "relative al sinistro."
    )


# ---------------------------------------------------------------------------
# SECTION 7: Italian legal disclaimer
# ---------------------------------------------------------------------------

ITALIAN_LEGAL_DISCLAIMER: str = (
    "La presente comunicazione non costituisce riconoscimento di responsabilità "
    "né impegno di indennizzo da parte della Compagnia assicuratrice. "
    "La verifica della copertura, dei massimali, delle franchigie e delle esclusioni "
    "di polizza resta di competenza esclusiva del liquidatore incaricato. "
    "Riferimenti normativi: Codice Civile Artt. 1882-1932 (contratto di assicurazione); "
    "D.Lgs. 209/2005 (Codice delle Assicurazioni Private); "
    "disposizioni IVASS vigenti."
)

IVASS_COMPLIANCE_NOTE: str = (
    "Procedura conforme alle disposizioni IVASS e al Codice delle Assicurazioni Private "
    "(D.Lgs. 209/2005)."
)


# ---------------------------------------------------------------------------
# Main policy functions — compatible with agent.py FunctionNode signatures
# ---------------------------------------------------------------------------

def validate_required_claim_fields(claim_value: Any) -> dict[str, Any]:
    """Validate minimum intake facts before coverage and evidence rules run."""

    claim = _as_model(ClaimNarrative, claim_value)
    missing: list[str] = []
    warnings: list[str] = []

    required_fields = {
        "policyholder_name": claim.policyholder_name,
        "policy_number": claim.policy_number,
        "contact_method": claim.contact_method,
        "date_of_loss": claim.date_of_loss,
        "loss_location": claim.loss_location,
        "loss_description": claim.loss_description,
    }
    for field_name, value in required_fields.items():
        if _blank(value):
            missing.append(field_name)

    if claim.estimated_loss_eur is None:
        warnings.append("Importo stimato del danno (€) non fornito.")

    if claim.codice_fiscale is None:
        warnings.append("Codice Fiscale non fornito — necessario per la liquidazione.")

    missing.extend(claim.missing_or_uncertain_facts)
    missing = _dedupe(missing)

    validation = FieldValidation(
        intake_status="missing_info" if missing else "valid",
        missing_fields=missing,
        warnings=_dedupe(warnings),
        ready_for_policy_review=not missing,
    )
    return validation.model_dump(exclude_none=True)


def apply_coverage_and_evidence_rules(
    claim_value: Any,
    validation_value: Any,
    classification_value: Any,
) -> dict[str, Any]:
    """Apply deterministic coverage, evidence, and first-pass routing rules — Italian market."""

    claim = _as_model(ClaimNarrative, claim_value)
    validation = _as_model(FieldValidation, validation_value)
    classification = _as_model(ClaimClassification, classification_value)

    findings: list[EvidenceRuleFinding] = []
    coverage_notes: list[str] = []
    required_docs: list[str] = []
    evidence_text = _all_evidence_text(claim)

    def add(
        rule_id: str,
        severity: str,
        message: str,
        required_action: str,
        document: str | None = None,
    ) -> None:
        findings.append(
            EvidenceRuleFinding(
                rule_id=rule_id,
                severity=severity,
                message=message,
                required_action=required_action,
                document=document,
            )
        )
        if document:
            required_docs.append(document)

    if validation.missing_fields:
        add(
            "INTAKE-001",
            "medium",
            "Dati obbligatori mancanti: la pratica non può essere assegnata in modo completo.",
            "collect_info",
        )

    # Check type-specific required documents (only "always" and "recommended" tags)
    claim_type = classification.claim_type
    for doc_name, reason, condition in TYPE_REQUIRED_DOCS.get(claim_type, TYPE_REQUIRED_DOCS["other"]):
        if condition in ("always", "recommended"):
            if not _document_provided(doc_name, claim):
                add(
                    "DOC-001",
                    "medium" if condition == "always" else "low",
                    f"Documento mancante o non confermato: {doc_name}. {reason}",
                    "collect_document",
                    doc_name,
                )

    # Conditional document checks based on narrative evidence
    for doc_name, reason, condition in TYPE_REQUIRED_DOCS.get(claim_type, TYPE_REQUIRED_DOCS["other"]):
        if condition == "police" and _has_any(evidence_text, [
            r"\bpolizia\b", r"\bcarabinieri\b", r"\bpolice\b", r"\bverbale\b",
            r"\bintervenuti\b", r"\bautorità\b",
        ]):
            if not _document_provided(doc_name, claim):
                add("DOC-002", "medium",
                    f"Le autorità risultano coinvolte. Documento richiesto: {doc_name}. {reason}",
                    "collect_document", doc_name)

        elif condition == "injury" and _positive_safety_concerns(claim):
            if not _document_provided(doc_name, claim):
                add("DOC-003", "high",
                    f"Lesioni personali dichiarate. Documento richiesto: {doc_name}. {reason}",
                    "collect_document", doc_name)

        elif condition == "repair" and _has_any(evidence_text, [
            r"\briparazion\w*\b", r"\bcarrozzeria\b", r"\bofficina\b",
            r"\bpreventivo\b", r"\bfattura\b", r"\brepair\b",
        ]):
            if not _document_provided(doc_name, claim):
                add("DOC-004", "medium",
                    f"Riparazione menzionata. Documento richiesto: {doc_name}. {reason}",
                    "collect_document", doc_name)

        elif condition == "workplace" and _has_any(evidence_text, [
            r"\blavoro\b", r"\binail\b", r"\bsul lavoro\b", r"\bcantiere\b",
        ]):
            if not _document_provided(doc_name, claim):
                add("DOC-005", "high",
                    f"Infortunio sul lavoro dichiarato. Documento richiesto: {doc_name}. {reason}",
                    "collect_document", doc_name)

    # High estimated loss
    if claim.estimated_loss_eur is not None and claim.estimated_loss_eur >= 25000:
        add(
            "LOSS-001",
            "high",
            "Importo stimato elevato — necessaria revisione tempestiva da parte del liquidatore.",
            "adjuster_review",
        )

    # ── Italian timing rules (Art. 1913 C.C.) ──
    loss_date = _parse_date(claim.date_of_loss)
    report_date = _parse_date(claim.reported_date)
    timeliness = check_reporting_timeliness(claim_type, loss_date, report_date)

    if timeliness["timeliness_status"] == "late_warning":
        add(
            "TIMING-ART1913-W",
            "medium",
            timeliness["message"],
            "collect_info",
        )
    elif timeliness["timeliness_status"] == "late_critical":
        add(
            "TIMING-ART1913-C",
            "high",
            timeliness["message"],
            "adjuster_review",
        )

    # ── Claim-type-specific coverage notes ──
    if claim_type == "rc_auto":
        coverage_notes.extend([
            "Verifica di responsabilità basata su modulo CAI/CID, verbali delle autorità e dinamica del sinistro.",
            "Non garantire la copertura prima dell'esame delle condizioni di polizza, franchigie e massimali.",
            "Verificare eleggibilità alla procedura di Risarcimento Diretto (CARD) ex Artt. 149-150 C.d.A.",
        ])
        # SECTION 6: Injury routing
        if _positive_safety_concerns(claim) or _has_positive_safety_language(evidence_text):
            add("SAFE-002", "urgent",
                "Lesioni personali dichiarate — instradamento all'ufficio liquidazione danni alla persona. "
                "Riferimento: circolare IVASS su micropermanenti.",
                "emergency_escalation")

    elif claim_type == "kasko":
        coverage_notes.extend([
            "Polizza Kasko — copertura danni propri al veicolo indipendentemente dalla responsabilità.",
            "Verificare franchigia, scoperto e limitazioni contrattuali.",
        ])

    elif claim_type == "furto_veicolo":
        coverage_notes.extend([
            "Furto o tentato furto del veicolo — denuncia alle autorità obbligatoria per legge.",
            "Verificare copertura furto nella polizza e eventuali clausole particolari.",
        ])
        if not _has_any(evidence_text, [r"\bdenuncia\b", r"\bpolizia\b", r"\bcarabinieri\b", r"\bquerela\b"]):
            add("FURTO-001", "high",
                "Sinistro di furto senza denuncia alle autorità — obbligatoria per legge.",
                "collect_document",
                ItalianDocumentType.denuncia_furto.value)

    elif claim_type == "incendio":
        coverage_notes.extend([
            "Incendio e scoppio — verificare copertura e causa dell'evento.",
            "Verbale dei Vigili del Fuoco necessario per determinare la causa.",
        ])
        # SECTION 6: Habitability
        if _has_any(evidence_text, [
            r"\binabitabile\b", r"\bevacuat\w*\b", r"\bnon agibile\b",
            r"\bsenza casa\b", r"\bsfollat\w*\b",
        ]):
            add("SAFE-HABIT-001", "urgent",
                "Abitazione non agibile a seguito dell'incendio — attivare protocollo 'pronto intervento'. "
                "La compagnia deve offrire alloggio di emergenza come da condizioni di polizza.",
                "emergency_escalation")

    elif claim_type == "acqua_condotta":
        coverage_notes.extend([
            "Danni da acqua condotta — verificare causa, provenienza e copertura in polizza.",
            "Importanza della tempestività della denuncia per evitare aggravamento dei danni.",
        ])
        # SECTION 6: Habitability
        if _has_any(evidence_text, [
            r"\binabitabile\b", r"\ballagat\w*\b", r"\bnon agibile\b",
            r"\bsenza casa\b", r"\bsfollat\w*\b", r"\belettric\w*\b",
            r"\bpericoloso\b", r"\bmuffa\b",
        ]):
            add("SAFE-HABIT-002", "urgent",
                "Abitazione potenzialmente non agibile a causa del danno da acqua — "
                "attivare protocollo 'pronto intervento'. La compagnia deve offrire "
                "alloggio di emergenza come da condizioni di polizza.",
                "emergency_escalation")

    elif claim_type == "infortuni":
        coverage_notes.extend([
            "Infortunio personale — verificare copertura infortuni nella polizza.",
            "Referto medico obbligatorio per la quantificazione del danno.",
        ])
        # SECTION 6: INAIL coordination
        if _has_any(evidence_text, [r"\blavoro\b", r"\binail\b", r"\bsul lavoro\b"]):
            add("INAIL-001", "high",
                "Infortunio sul lavoro dichiarato — necessario coordinamento con INAIL "
                "(Istituto Nazionale Assicurazione Infortuni sul Lavoro).",
                "adjuster_review")

    elif claim_type == "rc_generale":
        coverage_notes.extend([
            "Responsabilità Civile Generale — verificare massimali, franchigie ed esclusioni.",
            "In caso di atto di citazione o messa in mora, tempi di risposta stringenti.",
        ])
        # SECTION 6: Legal proceedings urgency
        if _has_any(evidence_text, [r"\batto di citazione\b", r"\bcitazione\b", r"\bmessa in mora\b"]):
            add("LEGAL-001", "high",
                "Procedimento legale in corso — urgenza per rispetto dei termini di prescrizione e decadenza.",
                "adjuster_review")

    elif claim_type == "tutela_legale":
        coverage_notes.extend([
            "Tutela legale — verificare copertura e massimale della polizza.",
            "Atto di citazione o provvedimento giudiziario necessario per l'attivazione.",
        ])
        # SECTION 6: Legal proceedings urgency
        if _has_any(evidence_text, [r"\batto di citazione\b", r"\bcitazione\b", r"\btribunale\b"]):
            add("LEGAL-002", "high",
                "Procedimento giudiziario in corso — i termini di prescrizione potrebbero essere in scadenza.",
                "adjuster_review")

    elif claim_type == "furto_casa":
        coverage_notes.extend([
            "Furto in abitazione — denuncia alle autorità obbligatoria per legge.",
            "Verificare copertura furto, massimali e sottolimiti per preziosi.",
        ])

    elif claim_type == "cristalli":
        coverage_notes.extend([
            "Rottura cristalli — verificare copertura specifica e carrozzeria convenzionata.",
        ])

    elif claim_type == "grandine":
        coverage_notes.extend([
            "Danni da grandine — verificare copertura eventi atmosferici.",
            "Bollettino meteorologico a supporto dell'evento.",
        ])

    elif claim_type == "viaggio":
        coverage_notes.extend([
            "Assicurazione viaggio — verificare copertura e limiti di polizza.",
            "Documentazione medica e ricevute necessarie per il rimborso.",
        ])

    else:
        coverage_notes.append(
            "Tipo di sinistro non classificato — instradare per triage umano "
            "dopo l'acquisizione dei dati minimi e della prova del danno."
        )

    # ── Determine routing ──
    if any(f.required_action == "emergency_escalation" for f in findings):
        route = "emergency_escalation"
    elif any(f.required_action == "siu_review" for f in findings):
        route = "special_investigation"
    elif validation.missing_fields or any(f.required_action == "collect_document" for f in findings):
        route = "needs_docs"
    else:
        route = "ready_for_adjuster"

    decision = CoverageEvidenceDecision(
        routing_decision=route,
        provisional_coverage_considerations=_dedupe(coverage_notes),
        required_documents=_dedupe(required_docs),
        findings=findings,
        audit_trail=[
            "Validati i campi obbligatori della pratica.",
            f"Sinistro classificato come {classification.claim_type} con gravità {classification.severity}.",
            "Applicate le regole deterministiche italiane: documenti, tempestività (Art. 1913 C.C.), "
            "lesioni, sicurezza e instradamento.",
            f"Instradamento iniziale selezionato: {route}.",
        ],
    )
    return decision.model_dump(exclude_none=True)


def generate_document_checklist(
    claim_value: Any,
    classification_value: Any,
    evidence_decision_value: Any,
) -> dict[str, Any]:
    """Generate an Italian claimant-facing checklist from deterministic document rules."""

    claim = _as_model(ClaimNarrative, claim_value)
    classification = _as_model(ClaimClassification, classification_value)
    evidence_decision = _as_model(CoverageEvidenceDecision, evidence_decision_value)
    required = set(evidence_decision.required_documents)

    items: list[DocumentChecklistItem] = []
    for doc_name, reason, condition in TYPE_REQUIRED_DOCS.get(
        classification.claim_type, TYPE_REQUIRED_DOCS["other"]
    ):
        provided = _document_provided(doc_name, claim)
        if condition == "always":
            priority = "required"
        elif doc_name in required:
            priority = "required"
        elif condition == "recommended":
            priority = "recommended"
        else:
            priority = "conditional"

        # Resolve ItalianDocumentType if possible
        italian_doc_type = None
        try:
            italian_doc_type = ItalianDocumentType(doc_name)
        except ValueError:
            pass

        items.append(
            DocumentChecklistItem(
                item=doc_name,
                reason=reason,
                priority=priority,
                already_provided=provided,
                italian_document_type=italian_doc_type,
            )
        )

    # Add injury-specific document for auto claims
    if classification.claim_type == "rc_auto" and _positive_safety_concerns(claim):
        items.append(
            DocumentChecklistItem(
                item="Nomi dei feriti e strutture sanitarie coinvolte",
                reason="Necessario per l'assegnazione urgente della pratica lesioni.",
                priority="required",
                already_provided=_has_any(
                    _all_evidence_text(claim),
                    [r"\bpronto soccorso\b", r"\bospedale\b", r"\bclinica\b"],
                ),
            )
        )

    checklist = DocumentChecklist(
        items=items,
        claimant_tip=(
            "Invii copie leggibili dei documenti richiesti. Se un documento non è ancora "
            "disponibile, indichi il motivo e la data prevista di consegna."
        ),
    )
    return checklist.model_dump(exclude_none=True)


# ---------------------------------------------------------------------------
# SECTION 5: Italian fraud signals (SIU — Servizio Investigazioni Underwriting)
# ---------------------------------------------------------------------------

def fraud_signal_and_safety_gate(
    claim_value: Any,
    validation_value: Any,
    classification_value: Any,
    evidence_decision_value: Any,
) -> dict[str, Any]:
    """Apply deterministic SIU, fraud-pattern, timing, and safety gates — Italian market."""

    claim = _as_model(ClaimNarrative, claim_value)
    validation = _as_model(FieldValidation, validation_value)
    classification = _as_model(ClaimClassification, classification_value)
    evidence_decision = _as_model(CoverageEvidenceDecision, evidence_decision_value)

    signals: list[FraudSafetySignal] = []
    evidence_text = _all_evidence_text(claim)
    claim_type = classification.claim_type

    def signal(
        signal_id: str,
        severity: str,
        message: str,
        route_to_siu: bool = False,
        route_to_emergency: bool = False,
    ) -> None:
        signals.append(
            FraudSafetySignal(
                signal_id=signal_id,
                severity=severity,
                message=message,
                route_to_siu=route_to_siu,
                route_to_emergency=route_to_emergency,
            )
        )

    # ── Basic timing validation ──
    loss_date = _parse_date(claim.date_of_loss)
    report_date = _parse_date(claim.reported_date)

    if loss_date and report_date and report_date < loss_date:
        signal(
            "TIMING-001",
            "high",
            "La data di denuncia risulta anteriore alla data del sinistro.",
            route_to_siu=True,
        )

    # ── Art. 1913 C.C. timeliness check ──
    timeliness = check_reporting_timeliness(claim_type, loss_date, report_date)
    if timeliness["timeliness_status"] == "late_critical":
        signal(
            "TIMING-ART1913",
            "high",
            f"Denuncia molto tardiva — rischio decadenza ex Art. 1915 C.C. "
            f"({timeliness.get('actual_days', '?')} giorni, termine: {timeliness['deadline_days']} giorni).",
            route_to_siu=True,
        )
    elif timeliness["timeliness_status"] == "late_warning":
        signal(
            "TIMING-ART1913-W",
            "medium",
            f"Denuncia tardiva ma in fase di warning "
            f"({timeliness.get('actual_days', '?')} giorni, termine: {timeliness['deadline_days']} giorni). "
            f"Monitorare.",
        )

    # ── HIGH SUSPICION — Italian SIU signals ──

    # Colpo di frusta (whiplash fraud — Italy = 60% of European whiplash claims)
    if claim_type == "rc_auto" and _has_any(evidence_text, [
        r"\bcervicalgia\b", r"\blombalgia\b", r"\bcolpo di frusta\b",
        r"\bwhiplash\b", r"\bdistorsione cervicale\b",
    ]):
        # Check for low-speed / no visible damage indicators
        if _has_any(evidence_text, [
            r"\bbassa velocità\b", r"\bnessun danno visibile\b",
            r"\bpochi danni\b", r"\bdanni minimi\b", r"\bsenza danni\b",
            r"\bammaccatura lieve\b", r"\bgraffio\b",
        ]):
            signal(
                "SIU-COLPO-FRUSTA",
                "high",
                "Pattern sospetto: cervicalgia/lombalgia dichiarata con danni visibili minimi al veicolo. "
                "L'Italia registra il 60% dei sinistri europei per colpo di frusta — segnale SIU prioritario.",
                route_to_siu=True,
            )

    # Tamponamento a catena sospetto
    if claim_type == "rc_auto" and _has_any(evidence_text, [
        r"\btamponamento\b", r"\ba catena\b", r"\brear.?end\b",
    ]):
        parties = claim.parties_involved
        injuries = claim.injuries_or_safety_concerns
        if len(parties) >= 3 or (len(injuries) >= 3 and _has_any(evidence_text, [
            r"\bbassa velocità\b", r"\blieve\b", r"\bminimo\b",
        ])):
            signal(
                "SIU-TAMPONAMENTO",
                "high",
                "Tamponamento a catena sospetto con 3+ persone coinvolte tutte con lesioni in impatto a bassa velocità.",
                route_to_siu=True,
            )

    # Incendio doloso pattern
    if claim_type == "incendio" and _has_any(evidence_text, [
        r"\bfinanziat\w*\b", r"\bleasing\b", r"\bpignor\w*\b",
        r"\bprecedent[ei] incend\w*\b", r"\bsequestro\b",
    ]):
        signal(
            "SIU-INCENDIO-DOLOSO",
            "high",
            "Pattern di incendio doloso: veicolo/bene finanziato, pignorato o con precedenti sinistri incendio.",
            route_to_siu=True,
        )

    # Furto con targa clonata
    if claim_type in ("furto_veicolo", "rc_auto") and _has_any(evidence_text, [
        r"\btarga clonat\w*\b", r"\btarga rubat\w*\b",
        r"\bclonazion\w*\b",
    ]):
        signal(
            "SIU-TARGA-CLONATA",
            "high",
            "Sinistro con targa dichiarata rubata o clonata — possibile collegamento con frode organizzata.",
            route_to_siu=True,
        )

    # Sinistro concordato (staged accident)
    if claim_type == "rc_auto" and _has_any(evidence_text, [
        r"\bstesso indirizzo\b", r"\bstesso broker\b", r"\bstessa carrozzeria\b",
        r"\bconoscenti\b", r"\bparent\w*\b", r"\bfamiliari\b",
        r"\bstesso agente\b",
    ]):
        signal(
            "SIU-CONCORDATO",
            "high",
            "Possibile sinistro concordato: le parti coinvolte condividono indirizzo, broker, "
            "agenzia o carrozzeria di riferimento — segnale di frode organizzata.",
            route_to_siu=True,
        )

    # ── MEDIUM SUSPICION signals ──

    # Late policy activation
    if _has_any(evidence_text, [
        r"\bpolizza recente\b", r"\bappena stipulat\w*\b",
        r"\bnuova polizza\b", r"\brecent\w* attivat\w*\b",
    ]):
        signal(
            "SIU-POLIZZA-RECENTE",
            "medium",
            "Polizza attivata poco prima del sinistro (meno di 30 giorni) — monitorare.",
        )

    # Multiple claims same broker
    if _has_any(evidence_text, [
        r"\bpiù sinistri\b", r"\bsinistri precedenti\b",
        r"\bstesso intermediario\b",
    ]):
        signal(
            "SIU-MULTI-BROKER",
            "medium",
            "Più sinistri dallo stesso intermediario/broker negli ultimi 12 mesi — monitorare.",
        )

    # Weekend/holiday claim
    if _has_any(evidence_text, [
        r"\bfine settimana\b", r"\bweekend\b", r"\bfestiv\w*\b",
        r"\bdomenica\b", r"\bsabato\b", r"\bfermata desolat\w*\b",
        r"\bzona isolat\w*\b",
    ]):
        signal(
            "SIU-WEEKEND-FESTIVO",
            "medium",
            "Sinistro dichiarato in un weekend/festivo in luogo isolato — difficile verifica.",
        )

    # Suspicious repair shop preference
    if _has_any(evidence_text, [
        r"\bcarrozzeria di fiducia\b", r"\bsolo a questa officina\b",
        r"\bnon convenzionat\w*\b", r"\binsiste su\b",
    ]):
        signal(
            "SIU-CARROZZERIA-SOSPETTA",
            "medium",
            "L'assicurato insiste su una carrozzeria specifica non convenzionata — possibile accordo.",
        )

    # Family-only witnesses
    if _has_any(evidence_text, [
        r"\btestimoni familiari\b", r"\btestimone.*(?:moglie|marito|figli[oa]?|parent\w*)\b",
        r"\bsolo parenti\b",
    ]):
        signal(
            "SIU-TESTIMONI-FAM",
            "medium",
            "Gli unici testimoni dichiarati sono familiari dell'assicurato.",
        )

    # ── LOW SUSPICION (informational) ──

    # Late reporting
    if timeliness["timeliness_status"] in ("late_warning", "late_critical"):
        signal(
            "SIU-DENUNCIA-TARDIVA",
            "low",
            f"Denuncia tardiva: {timeliness.get('actual_days', '?')} giorni dopo il sinistro "
            f"(termine: {timeliness['deadline_days']} giorni).",
        )

    # Vague description
    if _has_any(evidence_text, [
        r"\bnon ricordo\b", r"\bnon sono sicuro\b", r"\bforse\b",
        r"\bnon so\b", r"\bvago\b", r"\bnot sure\b", r"\bdon'?t remember\b",
    ]):
        signal(
            "SIU-DESCRIZIONE-VAGA",
            "low",
            "La descrizione del sinistro contiene elementi incerti o vaghi nonostante domande dirette.",
        )

    # ── Generic evidence/loss checks ──
    if (
        claim.estimated_loss_eur is not None
        and claim.estimated_loss_eur >= 10000
        and not claim.evidence_available
        and not claim.documents_mentioned
    ):
        signal(
            "EVID-001",
            "high",
            "Importo stimato elevato senza alcuna documentazione a supporto.",
            route_to_siu=True,
        )

    if claim_type in ("furto_veicolo", "furto_casa") and _has_any(
        evidence_text,
        [r"\bnessuna denuncia\b", r"\bnon ho denunciat\w*\b", r"\bsenza denuncia\b"],
    ):
        signal(
            "FURTO-002",
            "medium",
            "Sinistro di furto senza denuncia alle autorità — la denuncia è obbligatoria per legge.",
        )

    # ── Safety escalation ──
    if evidence_decision.routing_decision == "emergency_escalation" or any(
        f.required_action == "emergency_escalation" for f in evidence_decision.findings
    ):
        signal(
            "SAFETY-001",
            "urgent",
            "Problema di sicurezza, lesioni personali o inagibilità dell'abitazione — "
            "necessaria revisione umana immediata.",
            route_to_emergency=True,
        )

    if any(item in validation.missing_fields for item in ["date_of_loss", "loss_location", "loss_description"]):
        signal(
            "INTAKE-002",
            "medium",
            "Dati fondamentali del sinistro ancora mancanti — l'instradamento resta in fase di follow-up.",
        )

    # ── Final routing decision ──
    if any(s.route_to_emergency for s in signals):
        final_route = "emergency_escalation"
    elif any(s.route_to_siu for s in signals):
        final_route = "special_investigation"
    else:
        final_route = evidence_decision.routing_decision

    gate = FraudSafetyGate(
        final_routing_decision=final_route,
        signals=signals,
        audit_trail=evidence_decision.audit_trail
        + [
            "Applicati i segnali antifrode SIU italiani (colpo di frusta, tamponamento, "
            "incendio doloso, targa clonata, sinistro concordato).",
            "Verificata tempestività della denuncia ex Art. 1913 C.C.",
            f"Instradamento finale selezionato: {final_route}.",
        ],
    )
    return gate.model_dump(exclude_none=True)


# ---------------------------------------------------------------------------
# SECTION 8: Build final claim intake packet — Italian handoff
# ---------------------------------------------------------------------------

# Italian route label mapping
_ITALIAN_ROUTE_LABELS: dict[str, str] = {
    "ready_for_adjuster": "Pronto per assegnazione al liquidatore",
    "needs_docs": "In attesa della documentazione",
    "special_investigation": "Sospeso per indagine antifrode (SIU)",
    "emergency_escalation": "Escalation d'emergenza",
}

_ITALIAN_STATUS_LABELS: dict[str, str] = {
    "valid": "Completa",
    "missing_info": "Informazioni mancanti",
}


def build_claim_intake_packet(
    claim_value: Any,
    validation_value: Any,
    classification_value: Any,
    evidence_decision_value: Any,
    checklist_value: Any,
    fraud_gate_value: Any,
) -> dict[str, Any]:
    """Build the final Markdown claim intake packet — Italian market."""

    claim = _as_model(ClaimNarrative, claim_value)
    validation = _as_model(FieldValidation, validation_value)
    classification = _as_model(ClaimClassification, classification_value)
    evidence_decision = _as_model(CoverageEvidenceDecision, evidence_decision_value)
    checklist = _as_model(DocumentChecklist, checklist_value)
    fraud_gate = _as_model(FraudSafetyGate, fraud_gate_value)

    missing = _dedupe(validation.missing_fields)
    route = fraud_gate.final_routing_decision
    route_label = _ITALIAN_ROUTE_LABELS.get(route, route.replace("_", " ").title())
    status_label = _ITALIAN_STATUS_LABELS.get(validation.intake_status, validation.intake_status)
    claim_type_label = classification.claim_type.replace("_", " ").title()

    # Determine Italian claim status
    if route == "special_investigation":
        stato = ItalianClaimStatus.sospeso_siu.value
    elif route == "emergency_escalation":
        stato = ItalianClaimStatus.in_lavorazione.value
    elif missing or route == "needs_docs":
        stato = ItalianClaimStatus.in_attesa_documenti.value
    else:
        stato = ItalianClaimStatus.in_lavorazione.value

    # Timestamp
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Checklist lines — Italian
    checklist_lines = []
    for item in checklist.items:
        if item.already_provided:
            status = "✅ già fornito"
        elif item.priority == "required":
            status = "🔴 obbligatorio"
        elif item.priority == "recommended":
            status = "🟡 consigliato"
        else:
            status = "⚪ condizionale"
        checklist_lines.append(f"- [{status}] **{item.item}** — {item.reason}")

    if not checklist_lines:
        checklist_lines.append("- Nessun documento aggiuntivo richiesto dalle regole attuali.")

    missing_lines = [f"- {field}" for field in missing] or [
        "- Nessun campo obbligatorio mancante."
    ]
    coverage_lines = [
        f"- {note}" for note in evidence_decision.provisional_coverage_considerations
    ] or [
        "- La verifica della copertura richiede l'esame delle condizioni di polizza, "
        "franchigie, massimali ed esclusioni da parte del liquidatore."
    ]

    signal_lines = [
        f"- `{s.signal_id}` [{s.severity}] {s.message}"
        for s in fraud_gate.signals
    ] or ["- Nessun segnale antifrode o di emergenza rilevato."]

    finding_lines = [
        f"- `{f.rule_id}` [{f.severity}] {f.message}"
        for f in evidence_decision.findings
    ] or ["- Nessun rilievo generato dalle regole deterministiche."]

    # Italian handoff summary
    loss_date_formatted = _format_italian_date(_parse_date(claim.date_of_loss))
    estimated_loss_str = (
        f"{claim.estimated_loss_eur:,.2f} €"
        if claim.estimated_loss_eur is not None
        else "non indicato"
    )

    handoff = (
        f"{claim.policyholder_name or 'Assicurato non identificato'} ha denunciato un sinistro "
        f"di tipo {claim_type_label} verificatosi il {loss_date_formatted} "
        f"presso {claim.loss_location or 'luogo non specificato'}. "
        f"Descrizione: {claim.raw_narrative_summary or claim.loss_description}. "
        f"Importo stimato: {estimated_loss_str}."
    )

    claimant_next = _next_claimant_message(route, missing, evidence_decision.required_documents)

    audit_lines = [f"{idx}. {entry}" for idx, entry in enumerate(fraud_gate.audit_trail, start=1)]

    # Timeliness info
    loss_date = _parse_date(claim.date_of_loss)
    report_date = _parse_date(claim.reported_date)
    timeliness = check_reporting_timeliness(classification.claim_type, loss_date, report_date)
    timeliness_line = f"**Tempestività denuncia:** {timeliness['message']}"

    markdown = f"""# Fascicolo di Acquisizione Sinistro

**Data generazione:** {now_str}
**Tipo sinistro:** {claim_type_label}
**Stato acquisizione:** {status_label}
**Stato pratica:** {stato}
**Gravità:** {classification.severity.title()}
**Instradamento:** {route_label}

{timeliness_line}

## Informazioni Mancanti
{chr(10).join(missing_lines)}

## Elenco Documenti Richiesti
{chr(10).join(checklist_lines)}

## Considerazioni sulla Copertura
{chr(10).join(coverage_lines)}

## Avvertenza Legale
{ITALIAN_LEGAL_DISCLAIMER}

{IVASS_COMPLIANCE_NOTE}

## Riepilogo per il Liquidatore
{handoff}

## Prossimo Messaggio all'Assicurato
{claimant_next}

## Rilievi Deterministici
{chr(10).join(finding_lines)}

## Segnali Antifrode e di Sicurezza (SIU)
{chr(10).join(signal_lines)}

## Traccia di Audit
{chr(10).join(audit_lines)}
"""

    packet = ClaimIntakePacket(
        claim_type=classification.claim_type,
        intake_status=validation.intake_status,
        severity=classification.severity,
        routing_decision=route,
        stato_sinistro=ItalianClaimStatus(stato),
        missing_information=missing,
        required_documents=checklist.items,
        coverage_considerations=evidence_decision.provisional_coverage_considerations,
        adjuster_handoff_summary=handoff,
        claimant_next_message=claimant_next,
        audit_trail=fraud_gate.audit_trail,
        markdown=markdown,
    )
    return packet.model_dump(exclude_none=True)
