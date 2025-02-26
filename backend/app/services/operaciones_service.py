import os
import tempfile
import time
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
import pandas as pd
from sqlalchemy import text
from app import db
from app.models.operacion import Operacion
from app.services.base_service import BaseService
from app.utils.exceptions import ValidationError, ProcessingError

class OperacionesService(BaseService):
    def __init__(self):
        super().__init__(Operacion)

    @staticmethod
    def allowed_file(filename):
        if not filename or '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in current_app.config['ALLOWED_EXTENSIONS'] and len(filename) <= 255

    def process_excel_file(self, file_path):
        try:
            current_app.logger.info(f"Processing file: {file_path}")
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path, engine='openpyxl', dtype={'Phone Number 1': str, 'Phone Number 2': str})
            elif file_path.endswith('.xls'):
                df = pd.read_excel(file_path, engine='xlrd', dtype={'Phone Number 1': str, 'Phone Number 2': str})
            else:
                df = pd.read_csv(file_path, dtype={'Phone Number 1': str, 'Phone Number 2': str})

            df = df.dropna(how='all')
            required_columns = {'Date', 'Time', 'Phone Number 1', 'Phone Number 2', 'Amount'}
            if not required_columns.issubset(df.columns):
                raise ValidationError("El archivo no tiene las columnas requeridas")
            
            df = df.dropna(subset=required_columns)
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
            df['Time'] = pd.to_datetime(df['Time'], format='%H:%M', errors='coerce').dt.strftime('%H:%M')
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            df = df[df['Amount'].notna()]
            current_app.logger.info(f"Processed rows: {len(df)}")
            return df
        except Exception as e:
            current_app.logger.error(f"Error processing Excel: {str(e)}")
            raise ProcessingError(f"Error procesando archivo: {str(e)}")

    def _insert_operaciones(self, records):
        stmt = text("""
            INSERT OR IGNORE INTO operaciones (fecha, hora, nombre1, nombre2, monto)
            VALUES (:fecha, :hora, :nombre1, :nombre2, :monto)
        """)
        try:
            db.session.execute(stmt, [{
                'fecha': record[0],
                'hora': record[1],
                'nombre1': record[2],
                'nombre2': record[3],
                'monto': record[4]
            } for record in records])
            db.session.commit()
            return len(records)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database insert error: {str(e)}")
            raise ProcessingError(f"Error insertando registros: {str(e)}")

    def procesar_archivos(self, files):
        upload_id = f"upload_{int(time.time())}"
        current_app.logger.info(f"Iniciando carga con ID: {upload_id}")
        processed_files = []
        total_records = 0

        for file in files:
            if not file or not self.allowed_file(file.filename):
                continue

            filename = secure_filename(file.filename)
            temp_path = os.path.join(tempfile.gettempdir(), f"{upload_id}_{filename}")

            try:
                file.save(temp_path)
                df = self.process_excel_file(temp_path)
                records = []
                for _, row in df.iterrows():
                    record = (
                        str(row['Date']),
                        str(row['Time']),
                        str(row['Phone Number 1']).strip(),
                        str(row['Phone Number 2']).strip(),
                        float(row['Amount'])
                    )
                    records.append(record)

                registros_procesados = self._insert_operaciones(records)
                processed_files.append({
                    'nombre': filename,
                    'registros': registros_procesados
                })
                total_records += registros_procesados
                current_app.logger.info(f"Procesados {registros_procesados} registros de {filename}")
            except Exception as e:
                current_app.logger.error(f"Error procesando {filename}: {str(e)}")
                raise
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        return {
            "processed_files": processed_files,
            "total_records": total_records
        }

    def get_historico(self, filtros):
        """Obtiene el histórico de operaciones con filtros"""
        # Logueo para diagnóstico
        self.verificar_tabla()
        current_app.logger.info(f"DATABASE_URL: {current_app.config['SQLALCHEMY_DATABASE_URI']}")
        
        params = {}
        base_query = """
            WITH operaciones_filtradas AS (
                SELECT 
                    o.id,
                    o.fecha,
                    o.hora,
                    o.nombre1,
                    o.nombre2,
                    o.monto,
                    CASE 
                        WHEN :persona1 != '' AND (o.nombre1 = :persona1 OR o.nombre2 = :persona1)
                        THEN 
                            CASE WHEN o.nombre1 = :persona1 THEN o.nombre1 ELSE o.nombre2 END
                        ELSE o.nombre1
                    END as nombre1_ordenado,
                    CASE 
                        WHEN :persona1 != '' AND (o.nombre1 = :persona1 OR o.nombre2 = :persona1)
                        THEN 
                            CASE WHEN o.nombre1 = :persona1 THEN o.nombre2 ELSE o.nombre1 END
                        ELSE o.nombre2
                    END as nombre2_ordenado
                FROM operaciones o
                WHERE 1=1
        """
        
        persona1 = filtros.get('nombre1', '')
        params = {'persona1': persona1}

        # Construir condiciones WHERE solo si los filtros tienen valores
        where_clauses = []
        
        if persona1:  # Solo añadir si no está vacío
            where_clauses.append("(o.nombre1 = :nombre1 OR o.nombre2 = :nombre1)")
            params['nombre1'] = persona1
            
        if filtros.get('nombre2') and not filtros.get('nombre1'):
            persona2 = filtros.get('nombre2')
            where_clauses.append("(o.nombre1 = :nombre2 OR o.nombre2 = :nombre2)")
            params['nombre2'] = persona2
            
        if filtros.get('fecha_desde') and filtros.get('fecha_desde').strip():
            where_clauses.append("o.fecha >= :fecha_desde")
            params['fecha_desde'] = filtros['fecha_desde']
            
        if filtros.get('fecha_hasta') and filtros.get('fecha_hasta').strip():
            where_clauses.append("o.fecha <= :fecha_hasta")
            params['fecha_hasta'] = filtros['fecha_hasta']

        # Añadir cláusulas WHERE a la consulta
        if where_clauses:
            base_query += " AND " + " AND ".join(where_clauses)
        base_query += ")"

        # Consulta para obtener la cantidad total y suma de montos
        count_query = f"{base_query} SELECT COUNT(*) as total, SUM(monto) as total_monto FROM operaciones_filtradas"
        
        # Logueo para diagnóstico
        current_app.logger.info(f"Consulta base generada:\n{base_query} SELECT * FROM operaciones_filtradas")
        current_app.logger.info(f"Parámetros utilizados: {params}")
        
        # Obtener total de registros en la tabla para comparación
        total_operaciones = db.session.query(db.func.count()).select_from(Operacion).scalar()
        current_app.logger.info(f"Total de registros en la tabla `operaciones`: {total_operaciones}")
        
        # Ejecutar consulta de conteo
        count_result = db.session.execute(text(count_query), params).fetchone()
        total = count_result.total if count_result else 0
        
        # Manejar correctamente el valor NULL en total_monto
        total_monto = 0
        if count_result and count_result.total_monto is not None:
            total_monto = float(count_result.total_monto)
        
        current_app.logger.info(f"Resultado de `COUNT`: Total registros={total}, Total monto={total_monto}")
        
        # Obtener datos para la página actual
        page = int(filtros.get('page', 1))
        per_page = int(filtros.get('per_page', 10))
        offset = (page - 1) * per_page

        # Consulta final para los datos de la página
        final_query = f"""
            {base_query} 
            SELECT 
                f.id,
                datetime(f.fecha || ' ' || f.hora) as fecha_completa,
                f.nombre1_ordenado as nombre1,
                f.nombre2_ordenado as nombre2,
                f.monto,
                COALESCE(a1.nombre || ' ' || a1.apellido_paterno, f.nombre1_ordenado) as nombre1_display,
                COALESCE(a2.nombre || ' ' || a2.apellido_paterno, f.nombre2_ordenado) as nombre2_display
            FROM operaciones_filtradas f
            LEFT JOIN afiliados a1 ON f.nombre1_ordenado = a1.numero
            LEFT JOIN afiliados a2 ON f.nombre2_ordenado = a2.numero
            ORDER BY fecha_completa DESC 
            LIMIT :per_page OFFSET :offset
        """
        
        params.update({'per_page': per_page, 'offset': offset})
        result = db.session.execute(text(final_query), params)
        
        # Formatear resultados para la respuesta
        data = [{
            'id': row.id,
            'fecha': row.fecha_completa,
            'nombre1': row.nombre1_display,
            'nombre2': row.nombre2_display,
            'monto': row.monto
        } for row in result]
        
        current_app.logger.info(f"Registros obtenidos en la consulta final: {len(data)}")

        # Devolver respuesta formateada
        return {
            "data": data,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page if per_page > 0 else 1
            },
            "montoTotal": float(total_monto),
            "total": total
        }

    def delete_all(self):
        try:
            db.session.execute(text("DELETE FROM operaciones"))
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ProcessingError(f"Error eliminando operaciones: {str(e)}")
        
    def verificar_tabla(self):
        """Verifica la estructura y datos de la tabla operaciones"""
        try:
            # Verificar estructura
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('operaciones')
            current_app.logger.info(f"Columnas en tabla operaciones: {[col['name'] for col in columns]}")
            
            # Obtener primeros 5 registros para depuración
            ops = Operacion.query.limit(5).all()
            current_app.logger.info(f"Primeros 5 registros: {[op.to_dict() for op in ops]}")
            
            return True
        except Exception as e:
            current_app.logger.error(f"Error verificando tabla: {str(e)}")
            return False