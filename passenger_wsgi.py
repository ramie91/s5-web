import sys
import os

# Insérez le chemin vers le dossier de votre application
sys.path.insert(0, os.path.dirname(__file__))

# Chargez le fichier app.py et créez une instance de l'application
from app import app as application
