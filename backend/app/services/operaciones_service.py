from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from app import db
from app.models.operacion import Operacion
from app.services.base_service import BaseService
from sqlalchemy import and_

class OperacionesService(BaseService):
    def __init__(self):
        super().__init__(Operacion)

    def get_historico(self, filtros: Dict) -> Dict:
        """Obtiene el histórico de operaciones con filtros"""
        query = Operacion.query

        # Aplicar filtros
        if filtros.get('nombre1'):
            query = query.filter(
                (Operacion.nombre1 == filtros['nombre1']) |
                (Operacion.nombre2 == filtros['nombre1'])
            )
        
        if filtros.get('nombre2') and not filtros.get('nombre1'):
            query = query.filter(
                (Operacion.nombre1 == filtros['nombre2']) |
                (Operacion.nombre2 == filtros['nombre2'])
            )

        if filtros.get('fecha_desde'):
            query = query.filter(Operacion.fecha >= filtros['fecha_desde'])
        
        if filtros.get('fecha_hasta'):
            query = query.filter(Operacion.fecha <= filtros['fecha_hasta'])

        # Paginación
        page = int(filtros.get('page', 1))
        per_page = int(filtros.get('per_page', 10))
        pagination = query.order_by(Operacion.fecha.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'items': [item.to_dict() for item in pagination.items]
        }

    def procesar_archivo(self, df: pd.DataFrame) -> Dict:
        """Procesa un DataFrame de operaciones"""
        try:
            registros_procesados = 0
            
            for _, row in df.iterrows():
                operacion = Operacion(
                    fecha=datetime.strptime(str(row['Date']), '%Y-%m-%d').date(),
                    hora=datetime.strptime(str(row['Time']), '%H:%M').time(),
                    nombre1=str(row['Phone Number 1']).strip(),
                    nombre2=str(row['Phone Number 2']).strip(),
                    monto=float(row['Amount'])
                )
                db.session.add(operacion)
                registros_procesados += 1

            db.session.commit()
            
            return {
                'success': True,
                'message': f'Se procesaron {registros_procesados} registros',
                'registros_procesados': registros_procesados
            }
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f'Error al procesar archivo: {str(e)}')