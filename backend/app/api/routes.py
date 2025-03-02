from flask import jsonify, request, current_app
from werkzeug.utils import secure_filename
from app.api import bp
from app.services.operaciones_service import OperacionesService
from app.services import afiliados_service
from app.services import emparejamiento_service
from app.utils.exceptions import ValidationError, ProcessingError
from functools import wraps
from app.models.afiliado import Afiliado
from app import db

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
    afiliados_service.delete_all()
    return jsonify({"success": True, "message": "Todos los afiliados eliminados correctamente"})


@bp.route('/afiliados/crear', methods=['POST'])
@handle_errors
def crear_afiliado():
    """Crea un nuevo afiliado"""
    try:
        datos = request.json
        
        # Validar datos requeridos
        campos_requeridos = ['numero', 'nombre', 'apellido_paterno', 'apellido_materno', 'dni']
        for campo in campos_requeridos:
            if campo not in datos or not datos[campo]:
                raise ValidationError(f"El campo {campo} es requerido")
        
        # Verificar si ya existe un afiliado con el mismo número o DNI
        afiliado_existente = Afiliado.query.filter(
            (Afiliado.numero == datos['numero']) | 
            (Afiliado.dni == datos['dni'])
        ).first()
        
        if afiliado_existente:
            if afiliado_existente.numero == datos['numero']:
                raise ValidationError(f"Ya existe un afiliado con el número {datos['numero']}")
            else:
                raise ValidationError(f"Ya existe un afiliado con el DNI {datos['dni']}")
        
        # Crear nuevo afiliado
        nuevo_afiliado = Afiliado(
            numero=datos['numero'],
            nombre=datos['nombre'],
            apellido_paterno=datos['apellido_paterno'],
            apellido_materno=datos['apellido_materno'],
            dni=datos['dni'],
            email=datos.get('email', ''),
            estado=datos.get('estado', 'Activo')
        )
        
        db.session.add(nuevo_afiliado)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Afiliado creado correctamente",
            "data": nuevo_afiliado.to_dict()
        })
        
    except ValidationError as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error en crear_afiliado: {str(e)}")
        return jsonify({"success": False, "error": "Error al crear el afiliado"}), 500

@bp.route('/afiliados/<int:id>', methods=['PUT'])
@handle_errors
def actualizar_afiliado(id):
    """Actualiza un afiliado existente"""
    try:
        afiliado = Afiliado.query.get(id)
        if not afiliado:
            raise ValidationError("Afiliado no encontrado")
        
        datos = request.json
        
        # Validar datos requeridos
        campos_requeridos = ['numero', 'nombre', 'apellido_paterno', 'apellido_materno', 'dni']
        for campo in campos_requeridos:
            if campo not in datos or not datos[campo]:
                raise ValidationError(f"El campo {campo} es requerido")
        
        # Si cambia el número o DNI, verificar que no exista otro afiliado con esos valores
        if (datos['numero'] != afiliado.numero or datos['dni'] != afiliado.dni):
            afiliado_existente = Afiliado.query.filter(
                ((Afiliado.numero == datos['numero']) | (Afiliado.dni == datos['dni'])) &
                (Afiliado.id != id)
            ).first()
            
            if afiliado_existente:
                if afiliado_existente.numero == datos['numero']:
                    raise ValidationError(f"Ya existe otro afiliado con el número {datos['numero']}")
                else:
                    raise ValidationError(f"Ya existe otro afiliado con el DNI {datos['dni']}")
        
        # Actualizar campos
        afiliado.numero = datos['numero']
        afiliado.nombre = datos['nombre']
        afiliado.apellido_paterno = datos['apellido_paterno']
        afiliado.apellido_materno = datos['apellido_materno']
        afiliado.dni = datos['dni']
        afiliado.email = datos.get('email', '')
        afiliado.estado = datos.get('estado', 'Activo')
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Afiliado actualizado correctamente",
            "data": afiliado.to_dict()
        })
        
    except ValidationError as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error en actualizar_afiliado: {str(e)}")
        return jsonify({"success": False, "error": "Error al actualizar el afiliado"}), 500