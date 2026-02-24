#!/bin/bash

# ===================================================================
# SCRIPT DE SWITCH ENVIRONNEMENT - ALIMANAKA
# Place ce fichier à la racine du projet (ALIMANAKA/switch-env.sh)
# ===================================================================

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Récupère le répertoire du script (racine du projet)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Fonction d'aide
show_help() {
    echo -e "${BLUE}Usage:${NC} ./switch-env.sh [local|prod|status|help]"
    echo ""
    echo -e "${GREEN}local${NC}    → Passe en mode localhost (dev)"
    echo -e "${GREEN}prod${NC}     → Passe en mode production IP (10.5.120.15)"
    echo -e "${YELLOW}status${NC}   → Affiche l'environnement actuel"
    echo -e "${YELLOW}help${NC}     → Affiche cette aide"
    echo ""
}

# Fonction status
show_status() {
    echo -e "${BLUE}=== ENVIRONNEMENT ACTUEL ===${NC}"
    echo ""
    
    # Backend
    if [ -f "$PROJECT_DIR/backend/.env" ]; then
        echo -e "${GREEN}Backend .env:${NC}"
        grep "BACKEND_URL\|FRONTEND_URL\|ENVIRONMENT" "$PROJECT_DIR/backend/.env" 2>/dev/null | head -5
    else
        echo -e "${RED}Backend: aucun .env trouvé${NC}"
    fi
    
    echo ""
    
    # Frontend
    if [ -f "$PROJECT_DIR/frontend/.env" ]; then
        echo -e "${GREEN}Frontend .env:${NC}"
        cat "$PROJECT_DIR/frontend/.env"
    else
        echo -e "${RED}Frontend: aucun .env trouvé${NC}"
    fi
}

# Fonction switch local
switch_local() {
    echo -e "${YELLOW}🔄 Switch vers LOCALHOST...${NC}"
    
    # Vérifie que les templates existent
    if [ ! -f "$PROJECT_DIR/.env.local" ]; then
        echo -e "${RED}❌ Erreur: .env.local non trouvé à la racine${NC}"
        exit 1
    fi
    if [ ! -f "$PROJECT_DIR/frontend/.env.local" ]; then
        echo -e "${RED}❌ Erreur: frontend/.env.local non trouvé${NC}"
        exit 1
    fi
    
    # Copie les fichiers
    cp "$PROJECT_DIR/.env.local" "$PROJECT_DIR/backend/.env"
    cp "$PROJECT_DIR/frontend/.env.local" "$PROJECT_DIR/frontend/.env"
    
    echo -e "${GREEN}✅ Mode LOCALHOST activé !${NC}"
    echo -e "${BLUE}   Backend:${NC} http://localhost:8000"
    echo -e "${BLUE}   Frontend:${NC} http://localhost:5173"
    echo ""
    echo -e "${YELLOW}⚠️  Redémarre tes serveurs:${NC}"
    echo "   Backend:  python manage.py runserver"
    echo "   Frontend: npm run dev"
}

# Fonction switch prod
switch_prod() {
    echo -e "${YELLOW}🔄 Switch vers PRODUCTION IP...${NC}"
    
    # Vérifie que les templates existent
    if [ ! -f "$PROJECT_DIR/.env.production" ]; then
        echo -e "${RED}❌ Erreur: .env.production non trouvé à la racine${NC}"
        exit 1
    fi
    if [ ! -f "$PROJECT_DIR/frontend/.env.production" ]; then
        echo -e "${RED}❌ Erreur: frontend/.env.production non trouvé${NC}"
        exit 1
    fi
    
    # Copie les fichiers
    cp "$PROJECT_DIR/.env.production" "$PROJECT_DIR/backend/.env"
    cp "$PROJECT_DIR/frontend/.env.production" "$PROJECT_DIR/frontend/.env"
    
    echo -e "${GREEN}✅ Mode PRODUCTION IP activé !${NC}"
    echo -e "${BLUE}   Backend:${NC} http://10.5.120.15:4002"
    echo -e "${BLUE}   Frontend:${NC} http://10.5.120.15:4003"
    echo ""
    echo -e "${YELLOW}⚠️  Redémarre tes serveurs:${NC}"
    echo "   Backend:  python manage.py runserver 0.0.0.0:4002"
    echo "   Frontend: npm run dev -- --host 0.0.0.0 --port 4003"
}

# Gestion des arguments
case "$1" in
    local)
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
        echo -e "${RED}❌ Argument invalide: $1${NC}"
        show_help
        exit 1
        ;;
esac