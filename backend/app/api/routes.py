from flask import jsonify
from app.api import bp

@bp.route('/test', methods=['GET'])
def test():
    """Ruta de prueba para verificar que la API funciona"""
    return jsonify({'message': 'API funcionando correctamente'})