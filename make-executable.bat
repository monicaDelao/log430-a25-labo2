@echo off
echo Making deploy.sh executable...
git update-index --chmod=+x deploy.sh
echo Done! deploy.sh is now executable on Linux/Unix systems.
echo.
echo To use on VM:
echo   1. ssh log430@10.194.32.238
echo   2. cd ~/log430-a25-labo2
echo   3. ./deploy.sh
echo.
pause