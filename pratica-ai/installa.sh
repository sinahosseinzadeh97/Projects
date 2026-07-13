#!/usr/bin/env bash
# ============================================================
# PraticaAI — Script di installazione e avvio
# Versione: 1.0 | Mercato: Italia
# Uso: bash installa.sh
# ============================================================

set -euo pipefail

# --- Colors ---
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; RESET='\033[0m'

# --- Banner ---
clear
echo ""
echo -e "${BLUE}${BOLD}"
echo "  ██████╗ ██████╗  █████╗ ████████╗██╗ ██████╗ █████╗      █████╗ ██╗"
echo "  ██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██║██╔════╝██╔══██╗    ██╔══██╗██║"
echo "  ██████╔╝██████╔╝███████║   ██║   ██║██║     ███████║    ███████║██║"
echo "  ██╔═══╝ ██╔══██╗██╔══██║   ██║   ██║██║     ██╔══██║    ██╔══██║██║"
echo "  ██║     ██║  ██║██║  ██║   ██║   ██║╚██████╗██║  ██║    ██║  ██║██║"
echo "  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝"
echo -e "${RESET}"
echo -e "  ${BOLD}PraticaAI — Acquisizione Sinistri con Intelligenza Artificiale${RESET}"
echo -e "  ${YELLOW}Versione 1.0 | Mercato Italiano | GDPR Compliant${RESET}"
echo ""
echo "============================================================"
echo ""

# --- STEP 1: Check Docker ---
echo -e "${BOLD}[1/5] Verifica Docker...${RESET}"
if ! command -v docker &>/dev/null; then
  echo -e "${RED}✗ Docker non trovato.${RESET}"
  echo ""
  echo "  Installa Docker Desktop da: https://www.docker.com/products/docker-desktop/"
  echo "  Poi riavvia questo script."
  echo ""
  # Open browser on macOS
  if [[ "$OSTYPE" == "darwin"* ]]; then
    open "https://www.docker.com/products/docker-desktop/"
  fi
  exit 1
fi

if ! docker info &>/dev/null; then
  echo -e "${RED}✗ Docker è installato ma non in esecuzione.${RESET}"
  echo "  Avvia Docker Desktop e riprova."
  if [[ "$OSTYPE" == "darwin"* ]]; then
    open -a Docker
    echo "  Attendo che Docker si avvii..."
    sleep 8
  fi
  exit 1
fi
echo -e "${GREEN}✓ Docker disponibile ($(docker --version | cut -d' ' -f3 | tr -d ','))${RESET}"

# --- STEP 2: Check docker-compose ---
echo -e "${BOLD}[2/5] Verifica Docker Compose...${RESET}"
if ! command -v docker-compose &>/dev/null && ! docker compose version &>/dev/null 2>&1; then
  echo -e "${RED}✗ Docker Compose non trovato.${RESET}"
  echo "  Docker Compose è incluso in Docker Desktop (versione recente)."
  exit 1
fi
COMPOSE_CMD="docker compose"
command -v docker-compose &>/dev/null && COMPOSE_CMD="docker-compose"
echo -e "${GREEN}✓ Docker Compose disponibile${RESET}"

# --- STEP 3: Setup .env ---
echo -e "${BOLD}[3/5] Configurazione ambiente...${RESET}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠ File .env creato da .env.example${RESET}"
  else
    touch .env
    echo -e "${YELLOW}⚠ File .env creato vuoto${RESET}"
  fi
fi

# Check for GOOGLE_API_KEY
if ! grep -q "GOOGLE_API_KEY=." .env 2>/dev/null; then
  echo ""
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo -e "${BOLD}  Configurazione API Key richiesta${RESET}"
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo ""
  echo "  PraticaAI usa Google Gemini per l'agente vocale Sofia."
  echo "  Ottieni una chiave API gratuita su:"
  echo ""
  echo -e "  ${BLUE}https://aistudio.google.com/app/apikey${RESET}"
  echo ""
  if [[ "$OSTYPE" == "darwin"* ]]; then
    open "https://aistudio.google.com/app/apikey"
  fi
  echo -n "  Incolla qui la tua GOOGLE_API_KEY: "
  read -r API_KEY
  if [ -z "$API_KEY" ]; then
    echo -e "${RED}✗ API Key non fornita. Impossibile continuare.${RESET}"
    exit 1
  fi
  # Write to .env
  if grep -q "GOOGLE_API_KEY" .env; then
    sed -i.bak "s/GOOGLE_API_KEY=.*/GOOGLE_API_KEY=$API_KEY/" .env
  else
    echo "GOOGLE_API_KEY=$API_KEY" >> .env
  fi
  echo -e "${GREEN}✓ API Key salvata in .env${RESET}"
fi

# Generate SECRET_KEY if missing
if ! grep -q "SECRET_KEY=." .env 2>/dev/null; then
  SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || \
           openssl rand -hex 32)
  if grep -q "SECRET_KEY" .env; then
    sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$SECRET/" .env
  else
    echo "SECRET_KEY=$SECRET" >> .env
  fi
  echo -e "${GREEN}✓ SECRET_KEY generata automaticamente${RESET}"
fi

rm -f .env.bak
echo -e "${GREEN}✓ Configurazione completata${RESET}"

# --- STEP 4: Start containers ---
echo ""
echo -e "${BOLD}[4/5] Avvio PraticaAI...${RESET}"
echo "  Prima esecuzione: download immagini Docker (~2-3 minuti)"
echo "  Esecuzioni successive: avvio in ~15 secondi"
echo ""

$COMPOSE_CMD up --build -d

# --- STEP 5: Wait for health check ---
echo ""
echo -e "${BOLD}[5/5] Verifica avvio servizi...${RESET}"
MAX_WAIT=60
COUNT=0
echo -n "  In attesa "
until curl -sf http://localhost:4177/health > /dev/null 2>&1; do
  echo -n "."
  sleep 2
  COUNT=$((COUNT + 2))
  if [ $COUNT -ge $MAX_WAIT ]; then
    echo ""
    echo -e "${RED}✗ Timeout — i container non rispondono.${RESET}"
    echo "  Controlla i log: docker compose logs"
    exit 1
  fi
done
echo ""
echo -e "${GREEN}✓ PraticaAI è online!${RESET}"

# --- Done ---
echo ""
echo -e "${GREEN}${BOLD}"
echo "  ┌─────────────────────────────────────────────┐"
echo "  │                                             │"
echo "  │   ✓ PraticaAI avviata con successo!         │"
echo "  │                                             │"
echo "  │   App:      http://localhost:4177           │"
echo "  │   API docs: http://localhost:4177/docs      │"
echo "  │   Auth:     http://localhost:4177/auth/     │"
echo "  │   GDPR:     http://localhost:4177/gdpr/     │"
echo "  │                                             │"
echo "  │   Per fermare: docker compose down          │"
echo "  │                                             │"
echo "  └─────────────────────────────────────────────┘"
echo -e "${RESET}"

# Open browser automatically
sleep 1
if [[ "$OSTYPE" == "darwin"* ]]; then
  open "http://localhost:4177"
elif command -v xdg-open &>/dev/null; then
  xdg-open "http://localhost:4177"
fi
