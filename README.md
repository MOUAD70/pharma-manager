# PharmaManager 
Application de gestion de pharmacie — Développé dans le cadre du test technique 
SMARTHOLOL 
 
## Stack Technique - Backend : Django 4.x + Django REST Framework + PostgreSQL - Frontend : React.js (Vite) - Documentation API : Swagger (drf-spectacular) 
 
## Installation Backend 
```bash 
cd server 
python -m venv venv && source venv/bin/activate 
pip install -r requirements.txt 
cp .env.example .env  # Configurer les variables 
python manage.py migrate 
python manage.py loaddata fixtures/initial_data.json  # Données de test 
python manage.py runserver 
``` 
 
## Variables d'Environnement (.env) 
``` 
DEBUG=True 
SECRET_KEY=votre-secret-key 
DB_NAME=pharma_db 
DB_USER=postgres 
DB_PASSWORD=password 
DB_HOST=localhost 
DB_PORT=5432 
``` 
 
## Installation Frontend 
```bash 
cd client 
npm install 
cp .env.example .env 
npm run dev 
```