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
                df = pd.read_excel(file_path, engine='openpyxl')
            elif file_path.endswith('.xls'):
                df = pd.read_excel(file_path, engine='xlrd')
            else:
                df = pd.read_csv(file_path)

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
        params = []
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

        where_clauses = []
        if 'nombre1' in filtros:
            where_clauses.append("(o.nombre1 = :nombre1 OR o.nombre2 = :nombre1)")
            params['nombre1'] = persona1
        if 'nombre2' in filtros and 'nombre1' not in filtros:
            persona2 = filtros.get('nombre2')
            where_clauses.append("(o.nombre1 = :nombre2 OR o.nombre2 = :nombre2)")
            params['nombre2'] = persona2
        if 'fecha_desde' in filtros:
            where_clauses.append("o.fecha >= :fecha_desde")
            params['fecha_desde'] = filtros['fecha_desde']
        if 'fecha_hasta' in filtros:
            where_clauses.append("o.fecha <= :fecha_hasta")
            params['fecha_hasta'] = filtros['fecha_hasta']

        if where_clauses:
            base_query += " AND " + " AND ".join(where_clauses)
        base_query += ")"

        final_query = """
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
        """

        page = int(filtros.get('page', 1))
        per_page = int(filtros.get('per_page', 10))
        offset = (page - 1) * per_page

        count_query = f"{base_query} SELECT COUNT(*) as total, SUM(monto) as total_monto FROM operaciones_filtradas"
        count_result = db.session.execute(text(count_query), params).fetchone()
        total = count_result.total if count_result else 0
        total_monto = count_result.total_monto if count_result else 0

        full_query = f"{base_query} {final_query} ORDER BY fecha_completa DESC LIMIT :per_page OFFSET :offset"
        params.update({'per_page': per_page, 'offset': offset})
        result = db.session.execute(text(full_query), params)
        
        data = [{
            'id': row.id,
            'fecha': row.fecha_completa,
            'nombre1': row.nombre1_display,
            'nombre2': row.nombre2_display,
            'monto': row.monto
        } for row in result]

        return {
            "data": data,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page
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