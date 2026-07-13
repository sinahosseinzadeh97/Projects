# PraticaAI

**Acquisizione Sinistri con Intelligenza Artificiale**

> *"Dal telefono al fascicolo. In 5 minuti."*

---

## Cos'è PraticaAI

PraticaAI è una piattaforma di acquisizione sinistri basata su intelligenza artificiale vocale, progettata esclusivamente per il mercato assicurativo italiano. L'agente vocale **Sofia** gestisce l'intero processo FNOL (First Notice of Loss) al telefono, raccogliendo dati strutturati dall'assicurato in lingua italiana con registro formale *Lei*, e compilando automaticamente il fascicolo sinistro nel formato richiesto dal liquidatore.

A differenza delle soluzioni IVR tradizionali, PraticaAI non è un menu a scelta multipla: è una conversazione naturale. Sofia comprende il contesto, pone domande pertinenti in base al tipo di sinistro (RC Auto, Kasko, Furto, Incendio, RCG, Infortuni), applica le regole CARD e CONSAP in tempo reale, e segnala automaticamente indicatori SIU per potenziali frodi.

Il risultato? Un fascicolo completo — con dati anagrafici, circostanze, veicoli coinvolti, testimoni, e documentazione richiesta — pronto sulla scrivania del liquidatore in 5 minuti invece di 48 ore. Tutto in conformità GDPR, IVASS Reg. 40/2018, e normativa italiana vigente.

---

## Come funziona

```
┌─────────────────┐     ┌─────────────────────┐     ┌──────────────────────┐
│                 │     │                     │     │                      │
│  📞 CHIAMATA    │────▶│  🤖 SOFIA (AI)       │────▶│  📋 FASCICOLO        │
│                 │     │                     │     │                      │
│  L'assicurato   │     │  Raccoglie, valida  │     │  Il liquidatore      │
│  descrive il    │     │  e struttura i dati │     │  riceve il dossier   │
│  sinistro       │     │  in tempo reale     │     │  completo e validato │
│                 │     │                     │     │                      │
└─────────────────┘     └─────────────────────┘     └──────────────────────┘
```

1. **📞 L'assicurato chiama** e descrive il sinistro a voce, come farebbe con un operatore umano
2. **🤖 Sofia (AI) raccoglie, struttura e valida** tutti i dati necessari — tipo sinistro, parti coinvolte, circostanze, documenti
3. **📋 Il liquidatore riceve il fascicolo completo** — strutturato, validato, con segnalazioni SIU e indicazione CARD/CONSAP

---

## Funzionalità principali

| Funzionalità | Descrizione |
|---|---|
| 🗣️ **Agente vocale italiano (Sofia)** | Conversazione naturale in italiano con registro formale *Lei*, empatia calibrata, e terminologia assicurativa corretta |
| 🔍 **Riconoscimento tipo sinistro** | Classificazione automatica: RC Auto, Kasko, Furto/Rapina, Incendio, Atti vandalici, Eventi atmosferici, RCG, Infortuni |
| 🏛️ **Sistema CARD e CONSAP** | Applicazione automatica della Convenzione CARD con identificazione casi gestione diretta/indiretta e integrazione CONSAP |
| 🚨 **Segnali SIU in tempo reale** | Rilevamento automatico di 12+ indicatori di potenziale frode (incongruenze, precedenti sospetti, circostanze anomale) |
| 🔒 **Conformità GDPR Art. 13, 17, 30** | Informativa privacy automatica, diritto all'oblio, registro trattamenti, consenso esplicito documentato |
| 📜 **Conforme IVASS Reg. 40/2018** | Aderenza normativa completa per gestione sinistri da parte di sistemi automatizzati |
| 🗄️ **Database persistente** | PostgreSQL con schema ottimizzato per sinistri italiani (SQLite per sviluppo locale) |
| 🔐 **Autenticazione operatori** | Sistema JWT con ruoli (operatore, liquidatore, supervisore), sessioni sicure |
| 📊 **Dashboard liquidatore** | Cockpit operativo con vista sinistri in tempo reale, filtri, e dettaglio fascicolo |
| 🆘 **Protocollo emergenze** | Escalation automatica per emergenze sanitarie (118), abitabilità, e rischio immediato |
| 📄 **CAI/CID digitale** | Supporto Constatazione Amichevole di Incidente con raccolta dati strutturata |
| 🇮🇹 **Validazione dati italiani** | Codice Fiscale, Targa, Partita IVA — validati in tempo reale con regex e checksum |

---

## Avvio rapido (macOS / Linux)

### Prerequisiti

- **Docker Desktop** installato e in esecuzione — [Scarica qui](https://www.docker.com/products/docker-desktop/)
- **Chiave API Google Gemini** (gratuita) — [Ottienila su AI Studio](https://aistudio.google.com/app/apikey)

### Installazione con un click

```bash
# Doppio click su:
🚀 Avvia PraticaAI.command

# Oppure da terminale:
bash installa.sh
```

Lo script:
1. ✅ Verifica Docker e Docker Compose
2. ✅ Configura `.env` automaticamente
3. ✅ Chiede la Google API Key (solo la prima volta)
4. ✅ Genera `SECRET_KEY` crittografica
5. ✅ Avvia tutti i container
6. ✅ Apre il browser su `http://localhost:4177`

---

## Avvio manuale

```bash
# 1. Copia il file di configurazione
cp .env.example .env

# 2. Modifica .env con la tua chiave API
#    GOOGLE_API_KEY=la_tua_chiave_qui

# 3. Avvia con Docker Compose
docker compose up --build

# 4. Apri il browser
open http://localhost:4177
```

### Fermare l'applicazione

```bash
docker compose down
```

### Visualizzare i log

```bash
docker compose logs -f
```

---

## Struttura del progetto

```
pratica-ai/
├── 🚀 Avvia PraticaAI.command   # Launcher macOS — doppio-click per avviare
├── installa.sh                   # Script di installazione automatica
├── .env.example                  # Template variabili d'ambiente
├── docker-compose.yml            # Configurazione sviluppo locale
├── docker-compose.prod.yml       # Configurazione produzione (ECS)
├── Dockerfile                    # Immagine Docker multi-stage
├── requirements.txt              # Dipendenze Python
├── init.sql                      # Schema iniziale PostgreSQL
│
├── agent.py                      # Grafo ADK — logica sinistri e flusso conversazionale
├── schemas.py                    # Modelli dati italiani (Pydantic) — sinistri, veicoli, persone
├── policies.py                   # Regole business: CARD, CONSAP, SIU, IVASS, CLC
├── database.py                   # Layer persistenza — PostgreSQL/SQLite (SQLAlchemy async)
├── auth.py                       # Autenticazione JWT — ruoli operatore/liquidatore
├── gdpr.py                       # Conformità GDPR — informativa, consenso, oblio, registro
├── examples.py                   # Scenari di test e dati di esempio
├── privacy_notice_it.txt         # Informativa privacy completa (Art. 13 GDPR)
│
├── live_demo/
│   ├── server.py                 # Backend FastAPI + WebSocket audio bidirezionale
│   ├── index.html                # Cockpit operatore — interfaccia italiana
│   ├── app.js                    # Logica frontend — WebSocket, audio, stato sinistro
│   └── styles.css                # Tema dark professionale
│
├── nginx/
│   └── nginx.conf                # Reverse proxy + WebSocket upgrade + rate limiting
│
├── terraform/                    # Infrastruttura AWS Milan eu-south-1 (IaC)
│   ├── ecs.tf                    # ECS Fargate — container orchestration
│   ├── ecr.tf                    # ECR — registry immagini Docker
│   ├── rds.tf                    # RDS PostgreSQL — database gestito
│   ├── elasticache.tf            # ElastiCache Redis — sessioni e cache
│   ├── alb.tf                    # Application Load Balancer — HTTPS termination
│   ├── vpc.tf                    # VPC — rete privata isolata
│   ├── security_groups.tf        # Security Groups — regole firewall
│   ├── secrets.tf                # Secrets Manager — credenziali cifrate
│   ├── cloudwatch.tf             # CloudWatch — log, metriche, allarmi
│   ├── variables.tf              # Variabili Terraform
│   ├── outputs.tf                # Output infrastruttura
│   └── versions.tf               # Provider e backend state
│
├── scripts/
│   ├── deploy.sh                 # Deploy automatizzato su AWS ECS
│   └── terraform-init.sh         # Setup iniziale infrastruttura cloud
│
└── assets/                       # Risorse grafiche e documentazione
```

---

## Architettura tecnica

| Layer | Tecnologia | Funzione |
|---|---|---|
| **Agente vocale** | Google Gemini Live (`it-IT`) | Conversazione voce→voce, comprensione linguaggio naturale |
| **Framework agente** | Google ADK (Agent Development Kit) | Grafo conversazionale, gestione stato, tool calling |
| **Backend API** | FastAPI + WebSocket | API REST, streaming audio bidirezionale, health check |
| **Modelli dati** | Pydantic v2 | Validazione, serializzazione, schema sinistri italiani |
| **Database** | PostgreSQL 15 / SQLite (dev) | Persistenza sinistri, sessioni, audit log |
| **ORM** | SQLAlchemy 2.0 (async) | Mapping oggetti-relazionale asincrono |
| **Autenticazione** | JWT (python-jose) + bcrypt | Token bearer, ruoli, sessioni sicure |
| **Frontend** | HTML5 + Vanilla JS + CSS3 | Cockpit operatore, dark theme, responsive |
| **Reverse proxy** | Nginx | WebSocket upgrade, rate limiting, static files |
| **Container** | Docker + Docker Compose | Sviluppo locale e produzione |
| **Infrastruttura** | Terraform + AWS (eu-south-1 Milano) | ECS Fargate, RDS, ElastiCache, ALB, VPC |
| **CI/CD** | Script bash (`deploy.sh`) | Build, push ECR, deploy ECS rolling update |

---

## Conformità e sicurezza

### 🔒 GDPR (Regolamento UE 2016/679)

| Articolo | Implementazione |
|---|---|
| **Art. 13** — Informativa | Informativa privacy automatica letta da Sofia all'inizio della chiamata |
| **Art. 17** — Diritto all'oblio | Endpoint API per cancellazione completa dati personali |
| **Art. 30** — Registro trattamenti | Registro automatico di ogni trattamento dati con base giuridica |
| **Art. 7** — Consenso | Consenso esplicito raccolto e documentato con timestamp |
| **Art. 25** — Privacy by design | Minimizzazione dati, pseudonimizzazione, cifratura at rest |

### 📜 IVASS Reg. 40/2018

- Trasparenza sull'uso di sistemi automatizzati nella gestione sinistri
- Nessuna decisione automatizzata sulla copertura o risarcimento
- Possibilità di richiedere operatore umano in qualsiasi momento
- Documentazione completa del processo decisionale dell'agente

### 🏛️ Sicurezza infrastrutturale

- **Dati in territorio EU**: AWS Region `eu-south-1` (Milano)
- **Cifratura**: TLS 1.3 in transito, AES-256 at rest
- **Rete isolata**: VPC privata con subnet dedicate
- **Credenziali**: AWS Secrets Manager, rotazione automatica
- **Audit log**: Ogni azione tracciata in CloudWatch con retention configurabile
- **Rate limiting**: Protezione DDoS a livello Nginx e ALB

---

## Deploy in produzione (AWS)

```bash
# 1. Configura l'infrastruttura (una tantum)
bash scripts/terraform-init.sh

# 2. Deploy dell'applicazione
bash scripts/deploy.sh
```

L'infrastruttura Terraform crea:
- VPC con subnet pubbliche e private
- ECS Fargate (serverless containers)
- RDS PostgreSQL (Multi-AZ opzionale)
- ElastiCache Redis (sessioni)
- ALB con certificato SSL
- CloudWatch (log + allarmi)

---

## Pilota gratuito

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   🎯  PROGRAMMA PILOTA GRATUITO                         │
│                                                         │
│   Durata:     8 settimane                               │
│   Volume:     fino a 200 sinistri                       │
│   Include:    report ROI completo                       │
│   Supporto:   setup + training + assistenza tecnica     │
│                                                         │
│   Contatto:   info@pratica-ai.it                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Variabili d'ambiente

| Variabile | Obbligatoria | Descrizione |
|---|---|---|
| `GOOGLE_API_KEY` | ✅ | Chiave API Google Gemini per l'agente vocale |
| `SECRET_KEY` | ✅ | Chiave segreta per firma JWT (generata automaticamente da `installa.sh`) |
| `DATABASE_URL` | ❌ | URL database PostgreSQL (default: SQLite locale) |
| `DB_PASSWORD` | ❌ | Password database PostgreSQL (produzione) |
| `ENVIRONMENT` | ❌ | `development` o `production` (default: `development`) |

---

## Licenza e contatti

```
© 2026 PraticaAI — Tutti i diritti riservati

Contatto commerciale:  info@pratica-ai.it
Supporto tecnico:      tech@pratica-ai.it
```

---

<p align="center">
  <strong>PraticaAI</strong> — Acquisizione Sinistri con Intelligenza Artificiale 🇮🇹
</p>
