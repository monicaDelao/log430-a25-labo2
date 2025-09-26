@echo off
REM Script de déploiement manuel sur la VM (Windows)
REM Usage: deploy.bat

echo Déploiement de l'application LOG430...
echo VM: log430@10.194.32.238

REM Vérifier la connectivité
echo Test de connectivité...
ping -n 2 10.194.32.238 >nul
if errorlevel 1 (
    echo  VM non accessible
    exit /b 1
)

echo  VM accessible
echo.
echo  Pour déployer manuellement:
echo 1. ssh log430@10.194.32.238
echo 2. cd ~/log430-a25-labo2
echo 3. git pull origin main
echo 4. docker compose build
echo 5. docker compose up -d
echo.
echo  Application sera disponible sur: http://10.194.32.238:5000
pause