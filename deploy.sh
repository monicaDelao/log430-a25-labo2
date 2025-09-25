#!/bin/bash

# Script de déploiement pour log430-a25-labo2
# Usage: ./deploy.sh [build|restart|stop|logs|status]

set -e

PROJECT_DIR="$HOME/log430-a25-labo2"
cd "$PROJECT_DIR"

case "${1:-deploy}" in
    "build")
        echo " Construction des images Docker..."
        git pull origin main
        docker compose build
        docker compose up -d
        echo "Déploiement terminé!"
        ;;
    
    "restart")
        echo "Redémarrage de l'application..."
        docker compose restart store_manager
        echo "Application redémarrée!"
        ;;
    
    "stop")
        echo "Arrêt des services..."
        docker compose down
        echo "Services arrêtés!"
        ;;
    
    "logs")
        echo "Affichage des logs..."
        docker compose logs -f --tail=50
        ;;
    
    "status")
        echo "Statut des services:"
        docker compose ps
        echo ""
        echo "Test de connectivité:"
        curl -s -I http://localhost:5000 | head -1 || echo "Application non accessible"
        ;;
    
    "deploy"|*)
        echo "Déploiement complet..."
        git pull origin main
        docker compose build
        docker compose up -d
        echo ""
        echo "Vérification des services:"
        docker compose ps
        echo ""
        echo "Test de l'application:"
        sleep 3
        curl -s -I http://localhost:5000 | head -1 || echo "Application non accessible"
        echo ""
        echo " Déploiement terminé!"
        echo " Application accessible sur: http://10.194.32.238:5000"
        ;;
esac