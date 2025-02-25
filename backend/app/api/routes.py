from flask import jsonify, request, current_app
from werkzeug.utils import secure_filename
from app.api import bp
from app.services.operaciones_service import OperacionesService
from app.services import afiliados_service
from app.utils.exceptions import ValidationError, ProcessingError
from functools import wraps

operaciones_service = OperacionesService()

def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            current_app.logger.warning(f"Validation error: {e}")
            return jsonify({"error": str(e)}), 400
        except ProcessingError as e:
            current_app.logger.error(f"Processing error: {e}")
            return jsonify({"error": str(e)}), 422
        except Exception as e:
            current_app.logger.error(f"Unexpected error: {e}")
            return jsonify({"error": "Unexpected error"}), 500
    return wrapper

@bp.route('/upload', methods=['POST'])
@handle_errors
def upload_file():
    if 'file' not in request.files:
        raise ValidationError("No se encontró el archivo")
    
    files = request.files.getlist('file')
    valid_files = [file for file in files if file and operaciones_service.allowed_file(file.filename)]
    
    if not valid_files:
        raise ValidationError("Archivos no permitidos o inválidos")

    result = operaciones_service.procesar_archivos(valid_files)
    
    return jsonify({
        "success": True,
        "message": f"Se procesaron {len(result['processed_files'])} archivos con {result['total_records']} registros.",
        "processed_files": result['processed_files'],
        "total_records": result['total_records']
    })

@bp.route('/historico', methods=['POST'])
@handle_errors
def get_historico():
    filtros = request.get_json() or {}
    resultado = operaciones_service.get_historico(filtros)
    return jsonify({
        "success": True,
        "data": resultado['data'],
        "pagination": resultado['pagination'],
        "montoTotal": resultado['montoTotal'],
        "total": resultado['total']
    })

@bp.route('/delete/operaciones/<int:id>', methods=['DELETE'])
@handle_errors
def delete_operacion(id):
    if operaciones_service.delete(id):
        return jsonify({"success": True, "message": "Operación eliminada correctamente"})
    raise ValidationError("Operación no encontrada")

@bp.route('/delete_all', methods=['DELETE'])
@handle_errors
def delete_all():
    operaciones_service.delete_all()
    return jsonify({"success": True, "message": "Histórico eliminado correctamente"})