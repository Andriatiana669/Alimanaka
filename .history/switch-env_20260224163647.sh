#!/bin/bash

# ===================================================================
# SCRIPT DE SWITCH ENVIRONNEMENT - ALIMANAKA
# À placer à la racine du projet (ALIMANAKA/switch-env.sh)
# ===================================================================

# Couleurs pour l'affichage
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

# Fichiers de configuration
ROOT_ENV_LOCAL="$PROJECT_DIR/.env.local"
ROOT_ENV_PROD="$PROJECT_DIR/.env.production"
BACKEND_ENV="$PROJECT_DIR/backend/.env"
FRONTEND_ENV="$PROJECT_DIR/frontend/.env"
FRONTEND_ENV_LOCAL="$PROJECT_DIR/frontend/.env.local"
FRONTEND_ENV_PROD="$PROJECT_DIR/frontend/.env.production"

# Configuration des environnements
DEV_IP="127.0.0.1"
PROD_IP="10.5.120.15"
DEV_BACKEND_PORT="8000"
PROD_BACKEND_PORT="4000"
DEV_FRONTEND_PORT="5173"
PROD_FRONTEND_PORT="5173"

# ===================================================================
# FONCTIONS UTILITAIRES
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

check_files() {
    local missing=0
    
    if [ ! -f "$ROOT_ENV_LOCAL" ]; then
        print_error ".env.local manquant à la racine"
        missing=1
    fi
    
    if [ ! -f "$ROOT_ENV_PROD" ]; then
        print_error ".env.production manquant à la racine"
        missing=1
    fi
    
    if [ ! -f "$FRONTEND_ENV_LOCAL" ]; then
        print_error "frontend/.env.local manquant"
        missing=1
    fi
    
    if [ ! -f "$FRONTEND_ENV_PROD" ]; then
        print_error "frontend/.env.production manquant"
        missing=1
    fi
    
    if [ $missing -eq 1 ]; then
        exit 1
    fi
}

# ===================================================================
# FONCTIONS PRINCIPALES
# ===================================================================

show_help() {
    print_header
    echo -e "${BLUE}Usage:${NC} ./switch-env.sh [local|prod|status|help]"
    echo ""
    echo -e "${GREEN}local${NC}     → Passe en mode développement (localhost)"
    echo -e "${GREEN}prod${NC}      → Passe en mode production (10.5.120.15)"
    echo -e "${YELLOW}status${NC}    → Affiche l'environnement actuel"
    echo -e "${YELLOW}help${NC}      → Affiche cette aide"
    echo ""
    echo -e "${PURPLE}Configuration actuelle:${NC}"
    echo "  📍 Dev:  $DEV_IP:$DEV_BACKEND_PORT (backend) / :$DEV_FRONTEND_PORT (frontend)"
    echo "  📍 Prod: $PROD_IP:$PROD_BACKEND_PORT (backend) / :$PROD_FRONTEND_PORT (frontend)"
    echo ""
}

show_status() {
    print_header
    echo -e "${BLUE}=== ÉTAT DES FICHIERS D'ENVIRONNEMENT ===${NC}"
    echo ""
    
    # Backend
    if [ -f "$BACKEND_ENV" ]; then
        echo -e "${GREEN}📁 Backend .env:${NC}"
        echo "   ├─ ENVIRONMENT: $(grep "^ENVIRONMENT=" "$BACKEND_ENV" | cut -d'=' -f2 || echo 'non défini')"
        echo "   ├─ BACKEND_URL: $(grep "^BACKEND_URL=" "$BACKEND_ENV" | cut -d'=' -f2 || echo 'non défini')"
        echo "   └─ FRONTEND_URL: $(grep "^FRONTEND_URL=" "$BACKEND_ENV" | cut -d'=' -f2 || echo 'non défini')"
    else
        echo -e "${RED}📁 Backend .env: ${NC}Fichier manquant"
    fi
    
    echo ""
    
    # Frontend
    if [ -f "$FRONTEND_ENV" ]; then
        echo -e "${GREEN}📁 Frontend .env:${NC}"
        echo "   ├─ VITE_APP_ENV: $(grep "^VITE_APP_ENV=" "$FRONTEND_ENV" | cut -d'=' -f2 || echo 'non défini')"
        echo "   ├─ VITE_API_BASE_URL: $(grep "^VITE_API_BASE_URL=" "$FRONTEND_ENV" | cut -d'=' -f2 || echo 'non défini')"
        echo "   └─ VITE_FRONTEND_URL: $(grep "^VITE_FRONTEND_URL=" "$FRONTEND_ENV" | cut -d'=' -f2 || echo 'non défini')"
    else
        echo -e "${RED}📁 Frontend .env: ${NC}Fichier manquant"
    fi
    
    echo ""
    echo -e "${YELLOW}Pour redémarrer les serveurs:${NC}"
    echo "  Backend:  cd backend && python manage.py runserver"
    echo "  Frontend: cd frontend && npm run dev"
    echo ""
}

switch_local() {
    print_header
    print_warning "Bascule vers l'environnement LOCALHOST (développement)..."
    
    check_files
    
    # Copie des fichiers
    cp "$ROOT_ENV_LOCAL" "$BACKEND_ENV"
    cp "$FRONTEND_ENV_LOCAL" "$FRONTEND_ENV"
    
    print_success "Environnement LOCAL activé !"
    echo ""
    echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Backend:${NC}  http://$DEV_IP:$DEV_BACKEND_PORT"
    echo -e "${BLUE}   Frontend:${NC} http://$DEV_IP:$DEV_FRONTEND_PORT"
    echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Commandes pour lancer les serveurs:${NC}"
    echo "  📦 Backend:  cd backend && python manage.py runserver"
    echo "  🎨 Frontend: cd frontend && npm run dev"
    echo ""
    echo -e "${PURPLE}Ou en une ligne:${NC}"
    echo "  (backend) python manage.py runserver"
    echo "  (frontend) npm run dev"
    echo ""
}

switch_prod() {
    print_header
    print_warning "Bascule vers l'environnement PRODUCTION (10.5.120.15)..."
    
    check_files
    
    # Copie des fichiers
    cp "$ROOT_ENV_PROD" "$BACKEND_ENV"
    cp "$FRONTEND_ENV_PROD" "$FRONTEND_ENV"
    
    print_success "Environnement PRODUCTION activé !"
    echo ""
    echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Backend:${NC}  http://$PROD_IP:$PROD_BACKEND_PORT"
    echo -e "${BLUE}   Frontend:${NC} http://$PROD_IP:$PROD_FRONTEND_PORT"
    echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Commandes pour lancer les serveurs:${NC}"
    echo "  📦 Backend:  cd backend && python manage.py runserver 0.0.0.0:$PROD_BACKEND_PORT"
    echo "  🎨 Frontend: cd frontend && npm run dev -- --host 0.0.0.0 --port $PROD_FRONTEND_PORT"
    echo ""
    echo -e "${PURPLE}Ou en une ligne:${NC}"
    echo "  (backend) python manage.py runserver 0.0.0.0:$PROD_BACKEND_PORT"
    echo "  (frontend) npm run dev -- --host 0.0.0.0 --port $PROD_FRONTEND_PORT"
    echo ""
}

# ===================================================================
# POINT D'ENTRÉE PRINCIPAL
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
            show_help
        else
            print_error "Argument invalide: $1"
            show_help
        fi
        exit 1
        ;;
esac

exit 0