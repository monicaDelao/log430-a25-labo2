# 🚀 Guide de déploiement - Labo 02

## 📌 Déploiement manuel sur VM

### 1. Connexion à la VM
```bash
ssh log430@10.194.32.238
```

### 2. Navigation vers le projet
```bash
cd ~/log430-a25-labo2
```

### 3. Mise à jour du code
```bash
git pull origin main
```

### 4. Démarrage des services
```bash
# Construction des images Docker
docker compose build

# Démarrage en arrière-plan
docker compose up -d
```

### 5. Vérification du statut
```bash
# Vérifier les conteneurs en cours
docker compose ps

# Voir les logs si nécessaire
docker compose logs -f store_manager
```

### 6. Accès à l'application
- **URL locale VM** : `http://localhost:5000`
- **URL externe** : `http://10.194.32.238:5000` (si le port 5000 est ouvert dans le pare-feu)

## 🔧 Commandes utiles de maintenance

### Redémarrer l'application
```bash
docker compose restart store_manager
```

### Arrêter tous les services
```bash
docker compose down
```

### Voir les logs en temps réel
```bash
docker compose logs -f
```

### Nettoyer les conteneurs et images non utilisés
```bash
docker system prune -f
```

### Vérifier l'espace disque
```bash
df -h
docker system df
```

## 🔒 Configuration des secrets GitHub

Pour que le déploiement automatique fonctionne, configurez le secret suivant dans votre dépôt GitHub :

1. Allez dans **Settings > Secrets and variables > Actions**
2. Cliquez sur **New repository secret**
3. Nom : `VM_PASSWORD`
4. Valeur : Le mot de passe de l'utilisateur `log430` sur la VM

## 🧪 Tests en local sur la VM

```bash
cd ~/log430-a25-labo2/src
python -m pytest tests/ -v
```

## 📊 Monitoring

### Vérifier que les services sont actifs
```bash
# Vérifier MySQL
docker compose exec mysql mysqladmin -u labo02 -plabo02 ping

# Vérifier Redis
docker compose exec redis redis-cli ping

# Vérifier l'application web
curl -I http://localhost:5000
```

### Accéder aux bases de données
```bash
# MySQL
docker compose exec mysql mysql -u labo02 -plabo02 labo02_db

# Redis
docker compose exec redis redis-cli
```

## 🚨 Résolution de problèmes

### Port déjà utilisé
```bash
# Voir qui utilise le port 5000
sudo netstat -tulpn | grep :5000

# Arrêter le processus si nécessaire
sudo kill -9 <PID>
```

### Problèmes de connectivité base de données
```bash
# Redémarrer uniquement MySQL
docker compose restart mysql

# Redémarrer uniquement Redis  
docker compose restart redis
```

### Logs détaillés
```bash
# Logs de tous les services
docker compose logs

# Logs d'un service specific
docker compose logs mysql
docker compose logs redis
docker compose logs store_manager
```

## 📈 Pipeline CI/CD

Le pipeline GitHub Actions se déclenche automatiquement sur :
- **Push** vers la branche `main`
- **Pull requests**

### Étapes du pipeline :
1. **Tests** : Exécution avec MySQL et Redis en services
2. **Déploiement** : Déploiement automatique sur la VM (uniquement pour `main`)

### Variables d'environnement requises :
- `VM_PASSWORD` : Mot de passe pour l'accès SSH à la VM