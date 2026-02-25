#!/bin/bash

# ===================================================================
# SCRIPT DE SWITCH ENVIRONNEMENT - ALIMANAKA
# ===================================================================

# Couleurs pour affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Récupère le répertoire du script (racine du projet)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Fichiers de configuration racine
ROOT_ENV_LOCAL="$PROJECT_DIR/.env.local"
ROOT_ENV_PROD="$PROJECT_DIR/.env"

# Fichiers de destination
BACKEND_ENV="$PROJECT_DIR/backend/.env"
FRONTEND_ENV="$PROJECT_DIR/frontend/.env"

# ===================================================================
# FONCTIONS D'AFFICHAGE
# ===================================================================
print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                   ALIMANAKA - Switch Env                ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ===================================================================
# VERIFICATIONS
# ===================================================================
check_files() {
    local missing=0
    for file in "$ROOT_ENV_LOCAL" "$ROOT_ENV_PROD"; do
        if [ ! -f "$file" ]; then
            print_error "Fichier manquant: $file"
            missing=1
        fi
    done
    if [ $missing -eq 1 ]; then exit 1; fi
}

# ===================================================================
# FONCTIONS PRINCIPALES
# ===================================================================

# Affiche l'état actuel
show_status() {
    print_header
    echo -e "${BLUE}=== ÉTAT ACTUEL DES ENVIRONNEMENTS ===${NC}"
    echo ""
    if [ -f "$BACKEND_ENV" ]; then
        echo -e "${GREEN}📁 Backend .env:${NC}"
        grep -E "ENVIRONMENT|BACKEND_URL|FRONTEND_URL" "$BACKEND_ENV" || echo "non défini"
    else
        echo -e "${RED}Backend .env manquant${NC}"
    fi
    echo ""
    if [ -f "$FRONTEND_ENV" ]; then
        echo -e "${GREEN}📁 Frontend .env:${NC}"
        grep -E "VITE_APP_ENV|VITE_API_BASE_URL|VITE_FRONTEND_URL" "$FRONTEND_ENV" || echo "non défini"
    else
        echo -e "${RED}Frontend .env manquant${NC}"
    fi
    echo ""
}

# Switch vers LOCAL
switch_local() {
    print_header
    print_warning "Bascule vers l'environnement LOCAL (développement)..."
    check_files

    # Copie dans backend
    cp "$ROOT_ENV_LOCAL" "$BACKEND_ENV"

    # Crée frontend/.env local à partir du même fichier
    sed -e "s#BACKEND_URL=http://localhost:[0-9]*#BACKEND_URL=http://localhost:4000#" \
        -e "s#FRONTEND_URL=http://localhost:[0-9]*#FRONTEND_URL=http://localhost:4002#" \
        "$ROOT_ENV_LOCAL" > "$FRONTEND_ENV"

    print_success "Environnement LOCAL activé !"
    echo ""
    echo -e "${BLUE}Backend: http://localhost:4000${NC}"
    echo -e "${BLUE}Frontend: http://localhost:4002${NC}"
    echo ""
}

# Switch vers PROD
switch_prod() {
    print_header
    print_warning "Bascule vers l'environnement PRODUCTION..."
    check_files

    # Copie dans backend
    cp "$ROOT_ENV_PROD" "$BACKEND_ENV"

    # Crée frontend/.env prod à partir du même fichier
    sed -e "s#BACKEND_URL=http://.*:.*#BACKEND_URL=http://10.5.120.15:4000#" \
        -e "s#FRONTEND_URL=http://.*:.*#FRONTEND_URL=http://10.5.120.15:4002#" \
        "$ROOT_ENV_PROD" > "$FRONTEND_ENV"

    print_success "Environnement PRODUCTION activé !"
    echo ""
    echo -e "${BLUE}Backend: http://10.5.120.15:4000${NC}"
    echo -e "${BLUE}Frontend: http://10.5.120.15:4002${NC}"
    echo ""
}

# Affiche l'aide
show_help() {
    print_header
    echo -e "${BLUE}Usage:${NC} ./switch-env.sh [local|prod|status|help]"
    echo ""
    echo -e "${GREEN}local${NC}   → Passe en mode développement (localhost)"
    echo -e "${GREEN}prod${NC}    → Passe en mode production (10.5.120.15)"
    echo -e "${YELLOW}status${NC}  → Affiche l'environnement actuel"
    echo -e "${YELLOW}help${NC}    → Affiche cette aide"
    echo ""
}

# ===================================================================
# POINT D'ENTRÉE
# ===================================================================
case "$1" in
    local|dev|development)
        switch_local
        ;;
    prod|production)
        switch_prod
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        if [ -z "$1" ]; then
            print_error "Argument manquant"
        else
            print_error "Argument invalide: $1"
        fi
        show_help
        exit 1
        ;;
esac

exit 0