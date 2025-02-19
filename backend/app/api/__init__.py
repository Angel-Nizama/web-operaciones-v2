from flask import Blueprint

bp = Blueprint('api', __name__)

# Importar rutas al final para evitar importaciones circulares
from app.api import routes