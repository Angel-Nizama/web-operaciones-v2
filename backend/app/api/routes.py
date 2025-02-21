from flask import jsonify, request
from app.api import bp
from app.services import operaciones_service
import pandas as pd
from werkzeug.exceptions import BadRequest

@bp.route('/operaciones/historico', methods=['POST'])
def get_historico():
    """Obtiene el histórico de operaciones con filtros"""
    try:
        filtros = request.get_json() or {}
        resultado = operaciones_service.get_historico(filtros)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/operaciones/<int:id>', methods=['DELETE'])
def delete_operacion(id):
    """Elimina una operación por su ID"""
    try:
        if operaciones_service.delete(id):
            return jsonify({'message': 'Operación eliminada correctamente'})
        return jsonify({'error': 'Operación no encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/operaciones/upload', methods=['POST'])
def upload_operaciones():
    """Procesa archivo de operaciones"""
    if 'file' not in request.files:
        raise BadRequest('No se encontró el archivo')
    
    file = request.files['file']
    if not file.filename:
        raise BadRequest('No se seleccionó ningún archivo')

    try:
        # Leer el archivo con pandas
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        resultado = operaciones_service.procesar_archivo(df)
        return jsonify(resultado)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400