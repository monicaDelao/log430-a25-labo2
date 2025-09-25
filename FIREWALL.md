# 🔥 Configuration du pare-feu VM

## Ouvrir le port 5000 sur la VM Ubuntu

### Vérifier l'état actuel
```bash
sudo ufw status
```

### Ouvrir le port 5000
```bash
sudo ufw allow 5000/tcp
```

### Vérifier que la règle est ajoutée
```bash
sudo ufw status numbered
```

### Alternative : Ouvrir le port pour une IP spécifique
```bash
sudo ufw allow from YOUR_IP_ADDRESS to any port 5000
```

## Commandes utiles

### Activer le pare-feu (si pas déjà fait)
```bash
sudo ufw enable
```

### Voir toutes les règles
```bash
sudo ufw status verbose
```

### Supprimer une règle (si nécessaire)
```bash
sudo ufw delete allow 5000/tcp
```

### Tester la connectivité depuis votre machine
```bash
curl -I http://10.194.32.238:5000
```