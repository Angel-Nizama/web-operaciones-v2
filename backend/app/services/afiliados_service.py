from app import db
from app.models.afiliado import Afiliado
from app.services.base_service import BaseService
from app.utils.exceptions import ValidationError, ProcessingError
from flask import current_app
from sqlalchemy import text
import pandas as pd
import os
import tempfile
from werkzeug.utils import secure_filename

class AfiliadosService(BaseService):
    def __init__(self):
        super().__init__(Afiliado)
    
    @staticmethod
    def allowed_file(filename):
        """Verifica si el archivo tiene una extensión permitida y un nombre válido"""
        if not filename or '.' not in filename:
            return False
        
        ext = filename.rsplit('.', 1)[1].lower()
        return (
            ext in current_app.config['ALLOWED_EXTENSIONS'] and
            len(filename) <= 255
        )
    
    def process_excel_file(self, file_path):
        """Procesa un archivo Excel de afiliados"""
        try:
            current_app.logger.info(f"Procesando archivo de afiliados: {file_path}")
            
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path, engine='openpyxl')
            elif file_path.endswith('.xls'):
                df = pd.read_excel(file_path, engine='xlrd')
            else:
                df = pd.read_csv(file_path)
            
            # Eliminar filas vacías
            df = df.dropna(how='all')
            
            # Verificar columnas requeridas
            required_columns = {'Phone Number', 'Nombre', 'Apellido Paterno', 'Apellido Materno', 'DNI'}
            if not required_columns.issubset(df.columns):
                raise ValidationError(f"El archivo no tiene las columnas requeridas: {required_columns}")
            
            # Filtrar filas con datos completos
            df = df.dropna(subset=required_columns)
            
            # Limpiar y formatear campos
            df['Phone Number'] = df['Phone Number'].astype(str).str.strip()
            
            for col in ['Nombre', 'Apellido Paterno', 'Apellido Materno']:
                df[col] = df[col].astype(str).str.strip().str.title()
            
            # Asegurar formato del DNI
            df['DNI'] = df['DNI'].astype(str).str.strip()
            
            # Si existe la columna Email, limpiarla
            if 'Email' in df.columns:
                df['Email'] = df['Email'].astype(str).str.strip().str.lower()
            
            current_app.logger.info(f"Filas procesadas: {len(df)}")
            return df
            
        except Exception as e:
            current_app.logger.error(f"Error procesando Excel: {str(e)}")
            raise ProcessingError(f"Error procesando archivo: {str(e)}")
    
    def procesar_archivo_afiliados(self, file):
        """Procesa un archivo de afiliados y actualiza la base de datos"""
        if not file or not self.allowed_file(file.filename):
            raise ValidationError("Archivo no permitido")
        
        temp_path = None
        try:
            # Guardar archivo temporalmente
            filename = secure_filename(file.filename)
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            file.save(temp_path)
            
            # Procesar archivo
            df = self.process_excel_file(temp_path)
            
            # Insertar registros
            records_processed = 0
            for _, row in df.iterrows():
                # Crear o actualizar afiliado
                afiliado_data = {
                    'numero': str(row['Phone Number']).strip(),
                    'nombre': str(row['Nombre']).strip(),
                    'apellido_paterno': str(row['Apellido Paterno']).strip(),
                    'apellido_materno': str(row['Apellido Materno']).strip(),
                    'dni': str(row['DNI']).strip(),
                    'email': str(row['Email']).strip() if 'Email' in row else '',
                    'estado': 'Activo'  # Estado por defecto
                }
                
                # Buscar afiliado existente
                afiliado = Afiliado.query.filter_by(numero=afiliado_data['numero']).first()
                
                if afiliado:
                    # Actualizar afiliado existente
                    for key, value in afiliado_data.items():
                        setattr(afiliado, key, value)
                else:
                    # Crear nuevo afiliado
                    afiliado = Afiliado(**afiliado_data)
                    db.session.add(afiliado)
                
                records_processed += 1
            
            db.session.commit()
            current_app.logger.info(f"Procesados {records_processed} registros de afiliados")
            
            return {
                "success": True,
                "message": f"Se procesaron {records_processed} registros de afiliados.",
                "total_records": records_processed
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error en upload_afiliados: {str(e)}")
            raise ProcessingError(f"Error procesando archivo: {str(e)}")
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
    
    def get_afiliados(self, filtros=None):
        """Obtener lista de afiliados con filtros"""
        if filtros is None:
            filtros = {}
        
        query = Afiliado.query
        
        # Aplicar filtros
        if filtros.get('numero'):
            query = query.filter(Afiliado.numero.like(f"%{filtros['numero']}%"))
            
        if filtros.get('nombre'):
            search_term = f"%{filtros['nombre']}%"
            query = query.filter(
                Afiliado.nombre.like(search_term) | 
                Afiliado.apellido_paterno.like(search_term) | 
                Afiliado.apellido_materno.like(search_term)
            )
            
        if filtros.get('dni'):
            query = query.filter(Afiliado.dni.like(f"%{filtros['dni']}%"))
            
        if filtros.get('estado') and filtros['estado'] != "Todos":
            query = query.filter(Afiliado.estado == filtros['estado'])
        
        # Contar totales para estadísticas
        total = query.count()
        activos = query.filter(Afiliado.estado == 'Activo').count()
        
        # Paginación
        page = int(filtros.get('page', 1))
        per_page = int(filtros.get('per_page', 10))
        
        pagination = query.order_by(Afiliado.nombre, Afiliado.apellido_paterno)\
                         .paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            "success": True,
            "data": [afiliado.to_dict() for afiliado in pagination.items],
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page
            },
            "totalAfiliados": total,
            "afiliadosActivos": activos
        }
    
    def buscar_afiliado(self, texto, tipo='nombre'):
        """Buscar afiliado por texto y tipo"""
        if len(texto) < 2:
            return []
        
        if tipo == 'dni':
            afiliados = Afiliado.query.filter(Afiliado.dni.like(f"%{texto}%")).limit(10).all()
            return [{
                'numero': afiliado.numero,
                'nombre_completo': f"{afiliado.nombre} {afiliado.apellido_paterno} {afiliado.apellido_materno}".strip(),
                'valor_busqueda': afiliado.dni
            } for afiliado in afiliados]
            
        elif tipo == 'numero':
            afiliados = Afiliado.query.filter(Afiliado.numero.like(f"%{texto}%")).limit(10).all()
            return [{
                'numero': afiliado.numero,
                'nombre_completo': f"{afiliado.nombre} {afiliado.apellido_paterno} {afiliado.apellido_materno}".strip(),
                'valor_busqueda': afiliado.numero
            } for afiliado in afiliados]
            
        else:
            # Búsqueda por nombre
            search_term = f"%{texto}%"
            afiliados = Afiliado.query.filter(
                Afiliado.nombre.like(search_term) | 
                Afiliado.apellido_paterno.like(search_term) | 
                Afiliado.apellido_materno.like(search_term)
            ).limit(10).all()
            
            return [{
                'numero': afiliado.numero,
                'nombre_completo': f"{afiliado.nombre} {afiliado.apellido_paterno} {afiliado.apellido_materno}".strip(),
                'valor_busqueda': afiliado.nombre
            } for afiliado in afiliados]
        
    def delete_all(self):
        """Elimina todos los afiliados"""
        try:
            db.session.query(Afiliado).delete()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ProcessingError(f"Error eliminando afiliados: {str(e)}")

    
    def validar_afiliado(self, data, id=None):
        """Valida los datos de un afiliado"""
        errores = []
        
        # Validar campos requeridos
        campos_requeridos = ['numero', 'nombre', 'apellido_paterno', 'apellido_materno', 'dni']
        for campo in campos_requeridos:
            if campo not in data or not data[campo]:
                errores.append(f"El campo {campo} es requerido")
        
        if errores:
            return errores
        
        # Verificar unicidad de número y DNI
        filtro = (Afiliado.numero == data['numero']) | (Afiliado.dni == data['dni'])
        
        # Si es una actualización, excluir el afiliado actual
        if id:
            filtro = filtro & (Afiliado.id != id)
            
        afiliado_existente = Afiliado.query.filter(filtro).first()
        
        if afiliado_existente:
            if afiliado_existente.numero == data['numero']:
                errores.append(f"Ya existe un afiliado con el número {data['numero']}")
            else:
                errores.append(f"Ya existe un afiliado con el DNI {data['dni']}")
        
        return errores