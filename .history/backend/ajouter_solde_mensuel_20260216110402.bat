:: backend/ajouter_solde_mensuel.bat
@echo off
echo === Ajout solde mensuel - %date% %time% === >> D:\I-Famadika\Alimanaka\logs\solde.log

cd /d D:\I-Famadika\Alimanaka\backend

call venv\Scripts\activate.bat

python manage.py ajouter_solde_mensuel >> D:\I-Famadika\Alimanaka\logs\solde.log 2>&1

echo === Termine - %date% %time% === >> D:\I-Famadika\Alimanaka\logs\solde.log
echo. >> D:\I-Famadika\Alimanaka\logs\solde.log