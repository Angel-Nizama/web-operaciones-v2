from flask import jsonify, request, current_app
from werkzeug.utils import secure_filename
from app.api import bp
from app.services.operaciones_service import OperacionesService
from app.services import afiliados_service
from app.services import emparejamiento_service
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
    current_app.logger.info(f"Recibido request: {request.get_json()}")
    try:
        filtros = request.get_json() or {}
        resultado = operaciones_service.get_historico(filtros)
        return jsonify({
            "success": True,
            "data": resultado['data'],
            "pagination": resultado['pagination'],
            "montoTotal": resultado['montoTotal'],
            "total": resultado['total']
        })
    except Exception as e:
        current_app.logger.error(f"Error en get_historico: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

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

@bp.route('/upload_afiliados', methods=['POST'])
@handle_errors
def upload_afiliados():
    """Procesa archivo de afiliados"""
    if 'file' not in request.files:
        raise ValidationError("No se encontró el archivo")
    
    file = request.files['file']
    if not file or not file.filename:
        raise ValidationError("No se seleccionó ningún archivo")
    
    resultado = afiliados_service.procesar_archivo_afiliados(file)
    return jsonify(resultado)

@bp.route('/afiliados', methods=['POST'])
@handle_errors
def get_afiliados():
    """Obtiene lista de afiliados con filtros"""
    filtros = request.json or {}
    resultado = afiliados_service.get_afiliados(filtros)
    return jsonify(resultado)

@bp.route('/buscar_afiliado', methods=['POST'])
@handle_errors
def buscar_afiliado():
    """Busca afiliados por texto y tipo"""
    texto = request.json.get('texto', '').strip()
    tipo = request.json.get('tipo', 'nombre')
    
    resultados = afiliados_service.buscar_afiliado(texto, tipo)
    return jsonify(resultados)


@bp.route('/emparejador/afiliados', methods=['GET'])
@handle_errors
def get_afiliados_por_rango():
    """Obtiene afiliados para un rango específico"""
    rango_inicio = request.args.get('rango_inicio', type=float)
    rango_fin = request.args.get('rango_fin', type=float)
    
    if rango_inicio is None or rango_fin is None:
        raise ValidationError("Rango de montos requerido")
        
    return jsonify(emparejamiento_service.get_afiliados_por_rango(rango_inicio, rango_fin))

@bp.route('/emparejador/afiliados', methods=['POST'])
@handle_errors
def agregar_afiliado_rango():
    """Agrega un afiliado a un rango"""
    data = request.json
    return jsonify(emparejamiento_service.agregar_afiliado_rango(data))

@bp.route('/emparejador/afiliados/<int:id>', methods=['DELETE'])
@handle_errors
def eliminar_afiliado_rango(id):
    """Elimina un afiliado de un rango"""
    return jsonify(emparejamiento_service.eliminar_afiliado_rango(id))

@bp.route('/emparejador/afiliados/rango', methods=['DELETE'])
@handle_errors
def eliminar_afiliados_rango():
    """Elimina todos los afiliados de un rango específico"""
    rango_inicio = request.args.get('rango_inicio', type=float)
    rango_fin = request.args.get('rango_fin', type=float)
    
    if rango_inicio is None or rango_fin is None:
        raise ValidationError("Rango de montos requerido")
        
    return jsonify(emparejamiento_service.eliminar_afiliados_rango(rango_inicio, rango_fin))

@bp.route('/emparejador/afiliados/todos', methods=['DELETE'])
@handle_errors
def eliminar_todos_afiliados():
    """Elimina todos los afiliados de todos los rangos"""
    return jsonify(emparejamiento_service.eliminar_todos_afiliados())

@bp.route('/emparejador/calcular', methods=['POST'])
@handle_errors
def calcular_emparejamientos():
    """Calcula emparejamientos óptimos entre afiliados"""
    filtros = request.json or {}
    return jsonify(emparejamiento_service.calcular_emparejamientos(filtros))

@bp.route('/emparejador/detalles/<afiliado1>/<afiliado2>', methods=['GET'])
@handle_errors
def obtener_detalles_emparejamiento(afiliado1, afiliado2):
    """Obtiene detalles de un emparejamiento específico"""
    return jsonify(emparejamiento_service.obtener_detalles_emparejamiento(afiliado1, afiliado2))

@bp.route('/delete_all_afiliados', methods=['DELETE'])
@handle_errors
def delete_all_afiliados():
    """Elimina todos los afiliados"""
    try:
        db.session.query(Afiliado).delete()
        db.session.commit()
        return jsonify({"success": True, "message": "Todos los afiliados eliminados correctamente"})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error en delete_all_afiliados: {str(e)}")
        return jsonify({"error": str(e)}), 500