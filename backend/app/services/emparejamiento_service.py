# app/services/emparejamiento_service.py
from datetime import datetime
import random
import numpy as np
import pandas as pd
import json
from flask import current_app
from sqlalchemy import text
from app import db
from app.models.afiliado import Afiliado
from app.models.operacion import Operacion
from app.models.rango_afiliado import RangoAfiliado
from app.services.base_service import BaseService
from app.utils.exceptions import ValidationError, ProcessingError

class EmparejamientoService(BaseService):
    def __init__(self):
        super().__init__(RangoAfiliado)
    
    def get_afiliados_por_rango(self, rango_inicio, rango_fin):
        """Obtiene afiliados registrados en un rango específico"""
        try:
            # Consulta para obtener afiliados dentro del rango especificado
            rangos = RangoAfiliado.query.filter_by(
                rango_inicio=rango_inicio, 
                rango_fin=rango_fin
            ).join(
                Afiliado, 
                RangoAfiliado.numero_afiliado == Afiliado.numero
            ).with_entities(
                RangoAfiliado.id,
                RangoAfiliado.numero_afiliado,
                Afiliado.nombre,
                Afiliado.apellido_paterno,
                Afiliado.apellido_materno,
                RangoAfiliado.recibe_en,
                RangoAfiliado.envia_a
            ).order_by(
                Afiliado.nombre, 
                Afiliado.apellido_paterno
            ).all()
            
            # Formatear los resultados
            afiliados = [{
                'id': rango.id,
                'numero': rango.numero_afiliado,
                'nombre_completo': f"{rango.nombre} {rango.apellido_paterno} {rango.apellido_materno}",
                'recibe_en': rango.recibe_en,
                'envia_a': rango.envia_a
            } for rango in rangos]
            
            # Obtener total de afiliados únicos en el sistema
            total_afiliados = db.session.query(
                db.func.count(db.distinct(RangoAfiliado.numero_afiliado))
            ).scalar() or 0
            
            return {
                "success": True,
                "data": afiliados,
                "total_afiliados": total_afiliados
            }
        
        except Exception as e:
            current_app.logger.error(f"Error en get_afiliados_por_rango: {str(e)}")
            raise ProcessingError(f"Error obteniendo afiliados: {str(e)}")
    
    def agregar_afiliado_rango(self, data):
        """Agrega un afiliado a un rango específico"""
        try:
            numero = data.get('numero')
            rango_inicio = data.get('rango_inicio')
            rango_fin = data.get('rango_fin')
            recibe_en = data.get('recibe_en')
            envia_a = data.get('envia_a')
            
            # Validaciones
            if numero is None or rango_inicio is None or rango_fin is None or not recibe_en or not envia_a:
                raise ValidationError("Todos los campos son requeridos")
            
            # Verificar si ya existe en este rango
            existing = RangoAfiliado.query.filter_by(
                numero_afiliado=numero, 
                rango_inicio=rango_inicio, 
                rango_fin=rango_fin
            ).first()
            
            if existing:
                raise ValidationError("El afiliado ya está registrado en este rango")
            
            # Crear y guardar el nuevo registro
            nuevo_rango = RangoAfiliado(
                numero_afiliado=numero,
                rango_inicio=rango_inicio,
                rango_fin=rango_fin,
                recibe_en=recibe_en,
                envia_a=envia_a
            )
            
            db.session.add(nuevo_rango)
            db.session.commit()
            
            return {
                "success": True,
                "message": "Afiliado agregado correctamente"
            }
            
        except ValidationError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error en agregar_afiliado_rango: {str(e)}")
            raise ProcessingError(f"Error agregando afiliado: {str(e)}")
    
    def eliminar_afiliado_rango(self, id):
        """Elimina un afiliado de un rango específico"""
        try:
            rango = RangoAfiliado.query.get(id)
            if not rango:
                raise ValidationError("No se encontró el registro")
            
            db.session.delete(rango)
            db.session.commit()
            
            return {
                "success": True,
                "message": "Afiliado eliminado del rango correctamente"
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error en eliminar_afiliado_rango: {str(e)}")
            raise ProcessingError(f"Error eliminando afiliado: {str(e)}")
    
    def eliminar_afiliados_rango(self, rango_inicio, rango_fin):
        """Elimina todos los afiliados de un rango específico"""
        try:
            RangoAfiliado.query.filter_by(
                rango_inicio=rango_inicio, 
                rango_fin=rango_fin
            ).delete()
            
            db.session.commit()
            
            return {
                "success": True,
                "message": "Afiliados eliminados del rango correctamente"
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error en eliminar_afiliados_rango: {str(e)}")
            raise ProcessingError(f"Error eliminando afiliados: {str(e)}")
    
    def eliminar_todos_afiliados(self):
        """Elimina todos los afiliados de todos los rangos"""
        try:
            RangoAfiliado.query.delete()
            db.session.commit()
            
            return {
                "success": True,
                "message": "Todos los afiliados eliminados correctamente"
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error en eliminar_todos_afiliados: {str(e)}")
            raise ProcessingError(f"Error eliminando afiliados: {str(e)}")
    
    def calcular_emparejamientos(self, filtros):
        """Calcula emparejamientos óptimos entre afiliados"""
        try:
            # Extraer valores de filtros con valores por defecto
            dias_minimos = filtros.get('dias_minimos', 1)
            riesgo_maximo = filtros.get('riesgo_maximo', 50)
            monto_minimo = filtros.get('monto_minimo', 0)
            monto_maximo = filtros.get('monto_maximo', 0)
            usar_algoritmo_avanzado = filtros.get('usar_algoritmo_avanzado', False)
            
            # Obtener ponderaciones
            ponderaciones = filtros.get('ponderaciones', {
                'dias': 0.4,
                'diversidad': 0.25,
                'operaciones': 0.25,
                'patron': 0.1
            })
            
            # Obtener todos los afiliados con sus rangos
            rangos_query = db.session.query(
                RangoAfiliado,
                Afiliado.nombre,
                Afiliado.apellido_paterno
            ).join(
                Afiliado,
                RangoAfiliado.numero_afiliado == Afiliado.numero
            ).all()
            
            # Convertir a DataFrame para procesamiento
            rango_afiliados = pd.DataFrame([
                {
                    'numero_afiliado': r[0].numero_afiliado,
                    'nombre_completo': f"{r[1]} {r[2]}",
                    'rango_inicio': r[0].rango_inicio,
                    'rango_fin': r[0].rango_fin,
                    'recibe_en': r[0].recibe_en,
                    'envia_a': r[0].envia_a
                }
                for r in rangos_query
            ])
            
            # Obtener todas las operaciones
            operaciones_query = Operacion.query.with_entities(
                Operacion.fecha,
                Operacion.hora,
                Operacion.nombre1,
                Operacion.nombre2,
                Operacion.monto
            ).all()
            
            # Convertir a DataFrame
            operaciones = pd.DataFrame([
                {
                    'fecha': op.fecha,
                    'hora': op.hora,
                    'nombre1': op.nombre1,
                    'nombre2': op.nombre2,
                    'monto': op.monto
                }
                for op in operaciones_query
            ])
            
            # Si no hay datos suficientes, retornar lista vacía
            if rango_afiliados.empty or operaciones.empty:
                return {"success": True, "data": []}
            
            # Calcular emparejamientos
            if usar_algoritmo_avanzado:
                resultados = self._evaluar_emparejamientos_avanzado(
                    rango_afiliados,
                    operaciones,
                    dias_minimos,
                    riesgo_maximo,
                    monto_minimo,
                    monto_maximo,
                    ponderaciones
                )
            else:
                resultados = self._evaluar_emparejamientos(
                    rango_afiliados,
                    operaciones,
                    dias_minimos,
                    riesgo_maximo
                )
            
            # Aplicar filtros de monto
            if monto_minimo > 0 or monto_maximo > 0:
                resultados_filtrados = []
                for res in resultados:
                    monto = res.get('monto_asignado', 0)
                    if monto_minimo > 0 and monto < monto_minimo:
                        continue
                    if monto_maximo > 0 and monto > monto_maximo:
                        continue
                    resultados_filtrados.append(res)
                resultados = resultados_filtrados
            
            return {
                "success": True,
                "data": resultados
            }
            
        except Exception as e:
            current_app.logger.error(f"Error en calcular_emparejamientos: {str(e)}")
            raise ProcessingError(f"Error calculando emparejamientos: {str(e)}")
    
    def _evaluar_emparejamientos(self, rango_afiliados, operaciones, dias_minimos, riesgo_maximo):
        """
        Evalúa y genera emparejamientos entre afiliados considerando múltiples criterios.
        """
        resultados = []
        total_parejas = 0
        parejas_filtradas = 0

        try:
            # Convertir fechas y horas a datetime para cálculos
            operaciones['fecha'] = pd.to_datetime(operaciones['fecha'])
            if not operaciones.empty and 'hora' in operaciones.columns:
                operaciones['hora'] = operaciones['hora'].apply(
                    lambda x: str(x) + ':00' if len(str(x).split(':')) == 2 else str(x)
                )
                operaciones['fecha_completa'] = pd.to_datetime(
                    operaciones['fecha'].dt.strftime('%Y-%m-%d') + ' ' + operaciones['hora']
                )
            fecha_actual = datetime.now().date()

            # Consolidar los rangos por afiliado
            rangos_consolidados = {}
            for _, row in rango_afiliados.iterrows():
                afiliado = row['numero_afiliado']
                if afiliado not in rangos_consolidados:
                    rangos_consolidados[afiliado] = {
                        'nombre_completo': row['nombre_completo'],
                        'rangos': [],
                        'recibe_en': set(),
                        'envia_a': set()
                    }
                
                rangos_consolidados[afiliado]['rangos'].append({
                    'inicio': row['rango_inicio'],
                    'fin': row['rango_fin']
                })
                rangos_consolidados[afiliado]['recibe_en'].add(row['recibe_en'])
                rangos_consolidados[afiliado]['envia_a'].add(row['envia_a'])

            # Iterar sobre todas las posibles combinaciones de afiliados
            afiliados_list = list(rangos_consolidados.items())
            for i, (num_afiliado1, info1) in enumerate(afiliados_list):
                for num_afiliado2, info2 in afiliados_list[i+1:]:
                    total_parejas += 1
                    
                    # Evitar auto-emparejamientos
                    if num_afiliado1 == num_afiliado2:
                        parejas_filtradas += 1
                        continue

                    # Calcular el rango efectivo
                    rango_efectivo = self._calcular_rango_efectivo(info1['rangos'], info2['rangos'])
                    if not rango_efectivo:
                        parejas_filtradas += 1
                        continue

                    # Ajustar el rango máximo para Izipay (límite de 800)
                    if 'Izipay' in info1['recibe_en'] or 'Izipay' in info2['recibe_en']:
                        rango_efectivo['fin'] = min(rango_efectivo['fin'], 800)

                    if rango_efectivo['fin'] <= rango_efectivo['inicio']:
                        parejas_filtradas += 1
                        continue

                    # Obtener el historial de operaciones entre la pareja
                    if not operaciones.empty:
                        operaciones_pareja = operaciones[
                            ((operaciones['nombre1'] == num_afiliado1) & (operaciones['nombre2'] == num_afiliado2)) |
                            ((operaciones['nombre1'] == num_afiliado2) & (operaciones['nombre2'] == num_afiliado1))
                        ]
                    else:
                        operaciones_pareja = pd.DataFrame()

                    # Verificar el tiempo transcurrido desde la última operación
                    if not operaciones_pareja.empty:
                        ultima_operacion = operaciones_pareja['fecha'].max()
                        dias_desde_ultima = (fecha_actual - ultima_operacion.date()).days
                        if dias_desde_ultima < dias_minimos:
                            parejas_filtradas += 1
                            continue
                    else:
                        dias_desde_ultima = float('inf')  # Sin operaciones previas

                    # Calcular métricas
                    diversidad_1 = self._calcular_diversidad(operaciones, num_afiliado1)
                    diversidad_2 = self._calcular_diversidad(operaciones, num_afiliado2)
                    diversidad_minima = min(diversidad_1, diversidad_2)
                    afiliado_menor_diversidad = num_afiliado1 if diversidad_1 < diversidad_2 else num_afiliado2
                    
                    operaciones_minimas, afiliado_menor_ops = self._calcular_total_operaciones(
                        operaciones, 
                        num_afiliado1, 
                        num_afiliado2
                    )

                    # Calcular riesgo
                    riesgo = self._calcular_riesgo(
                        dias_desde_ultima if dias_desde_ultima != float('inf') else 1000,
                        diversidad_minima,
                        operaciones_minimas
                    )

                    if riesgo > riesgo_maximo:
                        parejas_filtradas += 1
                        continue

                    # Calcular monto sugerido
                    monto_sugerido = self._calcular_monto_sugerido(
                        operaciones_pareja, 
                        rango_efectivo['inicio'], 
                        rango_efectivo['fin']
                    )

                    # Agregar emparejamiento a resultados
                    resultados.append({
                        "afiliado1": info1['nombre_completo'],
                        "afiliado2": info2['nombre_completo'],
                        "dias_desde_ultima": dias_desde_ultima if dias_desde_ultima != float('inf') else "Sin operaciones previas",
                        "diversidad_minima": f"{diversidad_minima} ({rangos_consolidados[afiliado_menor_diversidad]['nombre_completo']})",
                        "operaciones_intermedias_minimas": f"{operaciones_minimas} ({rangos_consolidados[afiliado_menor_ops]['nombre_completo']})",
                        "monto_asignado": monto_sugerido,
                        "riesgo": round(riesgo, 2),
                        "pareja": [num_afiliado1, num_afiliado2]
                    })

            # Ordenar por nivel de riesgo
            resultados.sort(key=lambda x: x['riesgo'])

        except Exception as e:
            current_app.logger.error(f"Error evaluando emparejamientos: {str(e)}")
            raise ProcessingError(f"Error calculando emparejamientos: {str(e)}")

        return resultados

    def _evaluar_emparejamientos_avanzado(self, rango_afiliados, operaciones, dias_minimos, riesgo_maximo, 
                                        monto_minimo, monto_maximo, ponderaciones):
        """
        Versión avanzada del evaluador de emparejamientos con ponderaciones personalizadas
        y análisis de patrones de comportamiento.
        
        Args:
            rango_afiliados: DataFrame con afiliados y sus rangos
            operaciones: DataFrame con historial de operaciones
            dias_minimos: Mínimo de días desde la última operación
            riesgo_maximo: Máximo riesgo permitido (0-100)
            monto_minimo: Monto mínimo para filtrar resultados (opcional)
            monto_maximo: Monto máximo para filtrar resultados (opcional)
            ponderaciones: Dict con ponderaciones para el cálculo de riesgo
            
        Returns:
            list: Lista de resultados de emparejamiento
        """
        resultados = []
        total_parejas = 0
        parejas_filtradas = 0
        max_parejas_procesar = 10000  # Límite de seguridad para evitar bucles infinitos

        try:
            # Validamos que los DataFrames no estén vacíos
            if rango_afiliados.empty:
                current_app.logger.warning("No hay afiliados registrados en los rangos")
                return resultados
                
            # Convertir fechas y horas a datetime para cálculos
            if not operaciones.empty:
                try:
                    operaciones['fecha'] = pd.to_datetime(operaciones['fecha'], errors='coerce')
                    
                    if 'hora' in operaciones.columns:
                        # Aseguramos formato consistente para la hora
                        operaciones['hora'] = operaciones['hora'].apply(
                            lambda x: str(x) + ':00' if x and len(str(x).split(':')) == 2 else str(x) if x else '00:00:00'
                        )
                        
                        # Combinamos fecha y hora
                        operaciones['fecha_completa'] = pd.to_datetime(
                            operaciones['fecha'].dt.strftime('%Y-%m-%d') + ' ' + operaciones['hora'],
                            errors='coerce'
                        )
                    else:
                        # Si no hay columna hora, usamos solo la fecha
                        operaciones['fecha_completa'] = operaciones['fecha']
                except Exception as e:
                    current_app.logger.error(f"Error procesando fechas: {str(e)}")
                    # Creamos columnas vacías para evitar errores posteriores
                    operaciones['fecha_completa'] = None
            
            fecha_actual = datetime.now().date()

            # Consolidar los rangos por afiliado
            rangos_consolidados = {}
            for _, row in rango_afiliados.iterrows():
                afiliado = row['numero_afiliado']
                if afiliado not in rangos_consolidados:
                    rangos_consolidados[afiliado] = {
                        'nombre_completo': row['nombre_completo'],
                        'rangos': [],
                        'recibe_en': set(),
                        'envia_a': set()
                    }
                
                rangos_consolidados[afiliado]['rangos'].append({
                    'inicio': row['rango_inicio'],
                    'fin': row['rango_fin']
                })
                
                # Aseguramos que recibe_en y envia_a sean strings antes de añadirlos al set
                if row['recibe_en']:
                    rangos_consolidados[afiliado]['recibe_en'].add(str(row['recibe_en']))
                if row['envia_a']:
                    rangos_consolidados[afiliado]['envia_a'].add(str(row['envia_a']))

            # Verificamos que tengamos al menos dos afiliados para emparejar
            if len(rangos_consolidados) < 2:
                current_app.logger.warning("Se necesitan al menos 2 afiliados para calcular emparejamientos")
                return resultados

            # Iterar sobre todas las posibles combinaciones de afiliados
            afiliados_list = list(rangos_consolidados.items())
            for i, (num_afiliado1, info1) in enumerate(afiliados_list):
                # Control de límite de combinaciones para evitar bucles infinitos
                if total_parejas >= max_parejas_procesar:
                    current_app.logger.warning(f"Se alcanzó el límite de {max_parejas_procesar} parejas a procesar")
                    break
                    
                for num_afiliado2, info2 in afiliados_list[i+1:]:
                    total_parejas += 1
                    
                    # Control de límite por pareja
                    if total_parejas >= max_parejas_procesar:
                        break
                    
                    # Evitar auto-emparejamientos
                    if num_afiliado1 == num_afiliado2:
                        parejas_filtradas += 1
                        continue

                    # Calcular el rango efectivo con manejo de errores
                    try:
                        rango_efectivo = self._calcular_rango_efectivo(info1['rangos'], info2['rangos'])
                        if not rango_efectivo:
                            parejas_filtradas += 1
                            continue
                    except Exception as e:
                        current_app.logger.error(f"Error calculando rango efectivo para {num_afiliado1}-{num_afiliado2}: {str(e)}")
                        parejas_filtradas += 1
                        continue

                    # Ajustar el rango máximo para Izipay (límite de 800)
                    recibe_izipay = False
                    try:
                        if 'Izipay' in info1.get('recibe_en', set()) or 'Ambos' in info1.get('recibe_en', set()) or \
                        'Izipay' in info2.get('recibe_en', set()) or 'Ambos' in info2.get('recibe_en', set()):
                            recibe_izipay = True
                            rango_efectivo['fin'] = min(rango_efectivo['fin'], 800)
                    except Exception as e:
                        current_app.logger.error(f"Error verificando Izipay para {num_afiliado1}-{num_afiliado2}: {str(e)}")
                    
                    # Aplicar filtros de monto al rango efectivo
                    if monto_minimo and monto_minimo > 0:
                        rango_efectivo['inicio'] = max(rango_efectivo['inicio'], monto_minimo)
                    if monto_maximo and monto_maximo > 0:
                        rango_efectivo['fin'] = min(rango_efectivo['fin'], monto_maximo)

                    if rango_efectivo['fin'] <= rango_efectivo['inicio']:
                        parejas_filtradas += 1
                        continue

                    # Obtener el historial de operaciones entre la pareja con manejo de errores
                    try:
                        if not operaciones.empty:
                            operaciones_pareja = operaciones[
                                ((operaciones['nombre1'] == num_afiliado1) & (operaciones['nombre2'] == num_afiliado2)) |
                                ((operaciones['nombre1'] == num_afiliado2) & (operaciones['nombre2'] == num_afiliado1))
                            ]
                        else:
                            operaciones_pareja = pd.DataFrame()
                    except Exception as e:
                        current_app.logger.error(f"Error filtrando operaciones para {num_afiliado1}-{num_afiliado2}: {str(e)}")
                        operaciones_pareja = pd.DataFrame()

                    # Verificar el tiempo transcurrido desde la última operación
                    dias_desde_ultima = float('inf')  # Sin operaciones previas
                    try:
                        if not operaciones_pareja.empty and 'fecha' in operaciones_pareja.columns:
                            # Asegurar que tengamos fechas válidas
                            fechas_validas = operaciones_pareja['fecha'].dropna()
                            if not fechas_validas.empty:
                                ultima_operacion = fechas_validas.max()
                                if pd.notnull(ultima_operacion):
                                    dias_desde_ultima = (fecha_actual - ultima_operacion.date()).days
                                    
                                    # Filtrar por días mínimos
                                    if dias_desde_ultima < dias_minimos:
                                        parejas_filtradas += 1
                                        continue
                    except Exception as e:
                        current_app.logger.error(f"Error calculando días desde última operación: {str(e)}")
                        dias_desde_ultima = float('inf')

                    # Calcular métricas con manejo seguro de errores
                    try:
                        diversidad_1 = self._calcular_diversidad(operaciones, num_afiliado1)
                        diversidad_2 = self._calcular_diversidad(operaciones, num_afiliado2)
                        diversidad_minima = min(diversidad_1, diversidad_2)
                        afiliado_menor_diversidad = num_afiliado1 if diversidad_1 < diversidad_2 else num_afiliado2
                    except Exception as e:
                        current_app.logger.error(f"Error calculando diversidad: {str(e)}")
                        diversidad_minima = 0
                        afiliado_menor_diversidad = num_afiliado1
                    
                    try:
                        operaciones_minimas, afiliado_menor_ops = self._calcular_total_operaciones(
                            operaciones, 
                            num_afiliado1, 
                            num_afiliado2
                        )
                    except Exception as e:
                        current_app.logger.error(f"Error calculando total operaciones: {str(e)}")
                        operaciones_minimas = 0
                        afiliado_menor_ops = num_afiliado1
                    
                    # Análisis de patrones de comportamiento con manejo de errores
                    try:
                        patron_riesgo = self._evaluar_patron_operaciones({
                            'historial_operaciones': operaciones_pareja.to_dict('records') if not operaciones_pareja.empty else [],
                            'afiliado1': num_afiliado1,
                            'afiliado2': num_afiliado2
                        })
                    except Exception as e:
                        current_app.logger.error(f"Error evaluando patrón: {str(e)}")
                        patron_riesgo = 50  # Valor neutral por defecto

                    # Calcular riesgo con algoritmo avanzado
                    try:
                        riesgo = self._calcular_riesgo_mejorado(
                            {
                                'dias_desde_ultima': dias_desde_ultima if dias_desde_ultima != float('inf') else 1000,
                                'diversidad_minima': diversidad_minima,
                                'operaciones_intermedias': operaciones_minimas,
                                'patron_riesgo': patron_riesgo,
                                'historial_operaciones': operaciones_pareja.to_dict('records') if not operaciones_pareja.empty else []
                            },
                            {
                                'ponderacion_dias': ponderaciones.get('dias', 0.4),
                                'ponderacion_diversidad': ponderaciones.get('diversidad', 0.25),
                                'ponderacion_operaciones': ponderaciones.get('operaciones', 0.25),
                                'ponderacion_patron': ponderaciones.get('patron', 0.1)
                            }
                        )
                    except Exception as e:
                        current_app.logger.error(f"Error calculando riesgo: {str(e)}")
                        riesgo = 100  # Valor de máximo riesgo por defecto

                    # Filtrar por riesgo máximo
                    if riesgo > riesgo_maximo:
                        parejas_filtradas += 1
                        continue

                    # Calcular monto sugerido mejorado con manejo de errores
                    try:
                        monto_sugerido = self._calcular_monto_sugerido_mejorado(
                            operaciones_pareja, 
                            rango_efectivo['inicio'], 
                            rango_efectivo['fin'],
                            patron_riesgo
                        )
                        
                        # Si no se pudo calcular un monto sugerido, usar el método tradicional
                        if monto_sugerido is None:
                            monto_sugerido = self._calcular_monto_sugerido(
                                operaciones_pareja, 
                                rango_efectivo['inicio'], 
                                rango_efectivo['fin']
                            )
                            
                        # Si aún es None, usar un valor por defecto dentro del rango
                        if monto_sugerido is None:
                            monto_sugerido = (rango_efectivo['inicio'] + rango_efectivo['fin']) / 2
                    except Exception as e:
                        current_app.logger.error(f"Error calculando monto sugerido: {str(e)}")
                        # Usar promedio del rango como fallback
                        monto_sugerido = (rango_efectivo['inicio'] + rango_efectivo['fin']) / 2

                    # Formatear el valor de días desde la última operación para la visualización
                    dias_display = dias_desde_ultima
                    if dias_desde_ultima == float('inf'):
                        dias_display = "Sin operaciones previas"

                    # Agregar emparejamiento a resultados
                    resultados.append({
                        "afiliado1": info1['nombre_completo'],
                        "afiliado2": info2['nombre_completo'],
                        "dias_desde_ultima": dias_display,
                        "diversidad_minima": f"{diversidad_minima} ({rangos_consolidados[afiliado_menor_diversidad]['nombre_completo']})",
                        "operaciones_intermedias_minimas": f"{operaciones_minimas} ({rangos_consolidados[afiliado_menor_ops]['nombre_completo']})",
                        "monto_asignado": monto_sugerido,
                        "riesgo": round(riesgo, 2),
                        "pareja": [num_afiliado1, num_afiliado2]
                    })

            # Ordenar por nivel de riesgo
            resultados.sort(key=lambda x: x['riesgo'])
            
            current_app.logger.info(f"Emparejamiento completado: {len(resultados)} resultados de {total_parejas} combinaciones posibles")

        except Exception as e:
            current_app.logger.error(f"Error general en evaluación de emparejamientos: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            raise ProcessingError(f"Error calculando emparejamientos: {str(e)}")

        return resultados

    def _calcular_diversidad(self, operaciones, afiliado):
        """Calcula la diversidad de contrapartes para un afiliado"""
        if operaciones.empty:
            return 0
            
        ops_afiliado = operaciones[
            (operaciones['nombre1'] == afiliado) | 
            (operaciones['nombre2'] == afiliado)
        ]
        
        if ops_afiliado.empty:
            return 0
            
        contrapartes = set()
        for _, op in ops_afiliado.iterrows():
            contrapartes.add(op['nombre2'] if op['nombre1'] == afiliado else op['nombre1'])
            
        return len(contrapartes)
    
    def _calcular_total_operaciones(self, operaciones, afiliado1, afiliado2):
        """Calcula el número de operaciones desde la última operación mutua"""
        if operaciones.empty:
            return 0, afiliado1
            
        # Encontrar última operación entre ambos afiliados
        ops_mutuas = operaciones[
            ((operaciones['nombre1'] == afiliado1) & (operaciones['nombre2'] == afiliado2)) |
            ((operaciones['nombre1'] == afiliado2) & (operaciones['nombre2'] == afiliado1))
        ]
        
        if ops_mutuas.empty:
            # Si no hay operaciones mutuas previas, contar todas
            ops_a1 = len(operaciones[
                (operaciones['nombre1'] == afiliado1) | 
                (operaciones['nombre2'] == afiliado1)
            ])
            ops_a2 = len(operaciones[
                (operaciones['nombre1'] == afiliado2) | 
                (operaciones['nombre2'] == afiliado2)
            ])
        else:
            # Usar fecha_completa para comparación
            ultima_op_mutua = ops_mutuas['fecha_completa'].max()
            
            # Operaciones posteriores
            ops_posteriores = operaciones[operaciones['fecha_completa'] > ultima_op_mutua]
            
            ops_a1 = len(ops_posteriores[
                (ops_posteriores['nombre1'] == afiliado1) | 
                (ops_posteriores['nombre2'] == afiliado1)
            ])
            
            ops_a2 = len(ops_posteriores[
                (ops_posteriores['nombre1'] == afiliado2) | 
                (ops_posteriores['nombre2'] == afiliado2)
            ])
        
        # Determinar cuál tiene menos operaciones
        if ops_a1 <= ops_a2:
            return ops_a1, afiliado1
        return ops_a2, afiliado2
    
    def _calcular_riesgo(self, dias, diversidad, operaciones):
        """Calcula nivel de riesgo (0-100)"""
        # Normalizar factores
        riesgo_dias = 100 / (dias + 1)
        riesgo_diversidad = 100 / (diversidad + 1)
        riesgo_operaciones = 100 / (operaciones + 1)
        
        # Ponderación
        return (
            (riesgo_dias * 0.4) +
            (riesgo_diversidad * 0.3) +
            (riesgo_operaciones * 0.3)
        )
        
    def _calcular_riesgo_mejorado(self, datos_pareja, config):
        """
        Calcula nivel de riesgo avanzado (0-100) considerando múltiples factores
        
        Args:
            datos_pareja: Dict con datos de la pareja (dias, diversidad, operaciones, etc)
            config: Dict con configuración y ponderaciones
            
        Returns:
            float: Nivel de riesgo (0-100)
        """
        try:
            # Extraer datos con valores predeterminados seguros
            dias = datos_pareja.get('dias_desde_ultima', 1000)
            
            # Manejo seguro del valor de días
            if dias == "Sin operaciones previas":
                dias = 1000
            elif isinstance(dias, str) and dias.isdigit():
                dias = int(dias)
            elif not isinstance(dias, (int, float)):
                dias = 1000
                
            # Valores por defecto seguros para otras métricas
            diversidad_min = max(0, datos_pareja.get('diversidad_minima', 0))
            ops_intermedias = max(0, datos_pareja.get('operaciones_intermedias', 0))
            patron_riesgo = max(0, min(100, datos_pareja.get('patron_riesgo', 50)))
            
            # Obtener ponderaciones de la configuración con valores predeterminados
            pond_dias = max(0, min(1, config.get('ponderacion_dias', 0.4)))
            pond_diversidad = max(0, min(1, config.get('ponderacion_diversidad', 0.25)))
            pond_operaciones = max(0, min(1, config.get('ponderacion_operaciones', 0.25)))
            pond_patron = max(0, min(1, config.get('ponderacion_patron', 0.1)))
            
            # Normalizar ponderaciones para que sumen 1
            suma_ponderaciones = pond_dias + pond_diversidad + pond_operaciones + pond_patron
            if suma_ponderaciones > 0:
                pond_dias /= suma_ponderaciones
                pond_diversidad /= suma_ponderaciones
                pond_operaciones /= suma_ponderaciones
                pond_patron /= suma_ponderaciones
            else:
                # Si todas las ponderaciones son 0, usar valores predeterminados
                pond_dias, pond_diversidad, pond_operaciones, pond_patron = 0.4, 0.25, 0.25, 0.1
            
            # Calcular componentes de riesgo individual con protección contra división por cero
            
            # 1. Riesgo por días desde última operación (decaimiento exponencial)
            dias_factor = 1.0 / (1.0 + 0.1 * max(0, dias))
            riesgo_dias = dias_factor * 100
            
            # 2. Riesgo por diversidad de contrapartes
            div_factor = 1.0 / (1.0 + 0.2 * max(0, diversidad_min))
            riesgo_diversidad = div_factor * 100
            
            # 3. Riesgo por operaciones intermedias
            ops_factor = 1.0 / (1.0 + 0.15 * max(0, ops_intermedias))
            riesgo_operaciones = ops_factor * 100
            
            # 4. Usar el riesgo de patrón calculado externamente
            riesgo_patron = patron_riesgo
            
            # Cálculo de riesgo final con ponderaciones dinámicas
            riesgo_final = (
                (riesgo_dias * pond_dias) +
                (riesgo_diversidad * pond_diversidad) +
                (riesgo_operaciones * pond_operaciones) +
                (riesgo_patron * pond_patron)
            )
            
            # Normalizar a escala 0-100 y asegurar valores válidos
            return min(100, max(0, riesgo_final))
        
        except Exception as e:
            current_app.logger.error(f"Error en _calcular_riesgo_mejorado: {str(e)}")
            return 50  # Valor neutral por defecto en caso de error

    def _evaluar_patron_operaciones(self, datos_pareja):
        """
        Analiza patrones en las operaciones para detectar comportamientos inusuales
        """
        try:
            # Verificar que tengamos datos válidos
            historial = datos_pareja.get('historial_operaciones', [])
            
            if not historial or len(historial) < 2:
                return 50  # Valor neutro para historial escaso
            
            # Extraer montos válidos del historial
            montos = []
            for op in historial:
                if isinstance(op, dict) and 'monto' in op:
                    monto = op.get('monto')
                    if monto is not None and isinstance(monto, (int, float)) and monto > 0:
                        montos.append(monto)
            
            # Si no hay suficientes montos válidos, retornar valor neutro
            if len(montos) < 2:
                return 50
                
            # Analizar regularidad de montos (desviación estándar)
            media = sum(montos) / len(montos)
            if media <= 0:
                return 50
                
            # Calcular varianza y desviación estándar
            varianza = sum((x - media) ** 2 for x in montos) / len(montos)
            desviacion = varianza ** 0.5
                
            # Calcular coeficiente de variación (menor variación = más sospechoso)
            coef_var = desviacion / media
            
            # Invertir para obtener riesgo (menor variación = mayor riesgo)
            riesgo_variacion = 100 * (1 - min(1, coef_var))
                
            # Analizar regularidad temporal
            riesgo_temporal = self._analizar_regularidad_temporal(historial)
                
            # Combinar indicadores
            return (riesgo_variacion * 0.6) + (riesgo_temporal * 0.4)
        except Exception as e:
            current_app.logger.error(f"Error en _evaluar_patron_operaciones: {str(e)}")
            # En caso de error, devolver valor neutro
            return 50

    def _analizar_regularidad_temporal(self, historial):
        """
        Analiza la regularidad temporal de las operaciones
        Operaciones muy regulares pueden indicar comportamiento sospechoso
        """
        try:
            # Verificar datos de entrada
            if not historial or len(historial) < 2:
                return 50
                
            # Convertir fechas a objetos datetime
            import datetime
            fechas = []
            
            for op in historial:
                if not isinstance(op, dict) or 'fecha' not in op:
                    continue
                    
                fecha_str = op.get('fecha')
                if not fecha_str:
                    continue
                    
                # Procesar según el tipo de dato
                try:
                    if isinstance(fecha_str, datetime.date):
                        fechas.append(datetime.datetime.combine(fecha_str, datetime.datetime.min.time()))
                    elif isinstance(fecha_str, str):
                        for fmt in ['%Y-%m-%d', '%d/%m/%Y']:
                            try:
                                fecha = datetime.datetime.strptime(fecha_str, fmt)
                                fechas.append(fecha)
                                break
                            except ValueError:
                                continue
                except Exception:
                    # Ignorar fechas que no se pueden procesar
                    pass
            
            # Si no hay suficientes fechas válidas, retornar valor neutro
            if len(fechas) < 2:
                return 50
            
            # Ordenar fechas
            fechas.sort()
            
            # Calcular diferencias entre fechas consecutivas (en días)
            diferencias = []
            for i in range(len(fechas) - 1):
                if fechas[i+1] > fechas[i]:  # Asegurar que la diferencia es positiva
                    diferencias.append((fechas[i+1] - fechas[i]).days)
            
            # Si no hay suficientes diferencias válidas, retornar valor neutro
            if not diferencias:
                return 50
                
            # Calcular estadísticas de las diferencias
            media_dif = sum(diferencias) / len(diferencias)
            if media_dif <= 0:
                return 50
                
            # Calcular varianza y desviación estándar
            varianza_dif = sum((x - media_dif) ** 2 for x in diferencias) / len(diferencias)
            desviacion_dif = varianza_dif ** 0.5
                
            # Calcular coeficiente de variación temporal
            coef_var_temp = desviacion_dif / media_dif
                
            # Menor variación temporal = mayor riesgo (más regular = más sospechoso)
            # Dividir por 2 para ser menos estricto
            return 100 * (1 - min(1, coef_var_temp / 2))
        
        except Exception as e:
            current_app.logger.error(f"Error en _analizar_regularidad_temporal: {str(e)}")
            return 50  # Valor neutro en caso de error

    def _calcular_monto_sugerido(self, operaciones_pareja, rango_inicio, rango_fin, montos_excluir=None):
        """Calcula monto sugerido para una operación"""
        montos_excluir = montos_excluir or set()
        if not isinstance(montos_excluir, set):
            montos_excluir = set(montos_excluir)

        # Dividir el rango en tercios para priorizar montos más altos
        rango_size = rango_fin - rango_inicio
        tercio = rango_size / 3

        # Si el rango comienza en 0, priorizamos el último tercio
        if rango_inicio == 0:
            rango_inicio = max(rango_inicio, rango_fin - tercio)
        
        # Generamos puntos en el rango
        num_puntos = min(50, int(rango_size))
        montos_posibles = []
        
        # Distribuir con preferencia por valores más altos
        for i in range(num_puntos):
            factor = (i / num_puntos) ** 0.5  # Favorece valores altos
            monto = rango_inicio + (rango_fin - rango_inicio) * factor
            monto_redondeado = round(monto)
            if monto_redondeado not in montos_excluir:
                montos_posibles.append(monto_redondeado)

        if not montos_posibles:
            return None

        # Usar weights que favorecen montos más altos
        weights = [i + 1 for i in range(len(montos_posibles))]
        return random.choices(montos_posibles, weights=weights, k=1)[0]
    
    def _calcular_monto_sugerido_mejorado(self, operaciones_pareja, rango_inicio, rango_fin, factor_riesgo=50, montos_excluir=None):
        """
        Versión mejorada del cálculo de monto sugerido que tiene en cuenta el historial y el factor de riesgo
        """
        montos_excluir = montos_excluir or set()
        if not isinstance(montos_excluir, set):
            montos_excluir = set(montos_excluir)
        
        rango_size = rango_fin - rango_inicio
        
        # Si hay historial de operaciones, considerar los montos previos
        if not operaciones_pareja.empty:
            # Obtener montos previos
            montos_previos = operaciones_pareja['monto'].tolist()
            
            # Calcular estadísticas de montos
            if montos_previos:
                monto_medio = sum(montos_previos) / len(montos_previos)
                monto_desv = (sum((m - monto_medio) ** 2 for m in montos_previos) / len(montos_previos)) ** 0.5
                
                # Ajustar rango en función del historial y el riesgo
                # Si el riesgo es bajo, priorizar montos similares a los previos
                # Si el riesgo es alto, diversificar más el rango
                if factor_riesgo < 30:  # Riesgo bajo
                    # Centrar el rango alrededor del monto medio con un margen que depende de la desviación
                    nuevo_inicio = max(rango_inicio, monto_medio - 2 * monto_desv)
                    nuevo_fin = min(rango_fin, monto_medio + 2 * monto_desv)
                    
                    # Evitar que el rango sea demasiado pequeño
                    if nuevo_fin - nuevo_inicio < rango_size * 0.2:
                        margin = rango_size * 0.1
                        nuevo_inicio = max(rango_inicio, monto_medio - margin)
                        nuevo_fin = min(rango_fin, monto_medio + margin)
                    
                    rango_inicio, rango_fin = nuevo_inicio, nuevo_fin
        
        # Número de puntos a generar
        num_puntos = min(50, int(rango_size))
        montos_posibles = []
        
        # Ajustar la distribución según el factor de riesgo
        # Con riesgo bajo (< 30), preferir valores cercanos a la media
        # Con riesgo medio (30-70), distribución uniforme
        # Con riesgo alto (> 70), preferir valores extremos
        if factor_riesgo < 30:
            # Distribución centrada (preferencia por valores medios del rango)
            for i in range(num_puntos):
                # Usar distribución beta centrada
                factor = 0.5 + (i / num_puntos - 0.5) * 0.8  # Se concentra cerca de 0.5
                monto = rango_inicio + (rango_fin - rango_inicio) * factor
                monto_redondeado = round(monto)
                if monto_redondeado not in montos_excluir:
                    montos_posibles.append(monto_redondeado)
        elif factor_riesgo > 70:
            # Distribución bimodal (preferencia por extremos)
            for i in range(num_puntos):
                # Usar distribución que prefiere valores extremos
                if i < num_puntos / 2:
                    factor = (i / (num_puntos / 2)) * 0.3  # Cercanos al inicio
                else:
                    factor = 0.7 + ((i - num_puntos / 2) / (num_puntos / 2)) * 0.3  # Cercanos al fin
                monto = rango_inicio + (rango_fin - rango_inicio) * factor
                monto_redondeado = round(monto)
                if monto_redondeado not in montos_excluir:
                    montos_posibles.append(monto_redondeado)
        else:
            # Distribución uniforme con ligera preferencia por valores altos
            for i in range(num_puntos):
                factor = (i / num_puntos) ** 0.6  # Ligera preferencia por valores altos
                monto = rango_inicio + (rango_fin - rango_inicio) * factor
                monto_redondeado = round(monto)
                if monto_redondeado not in montos_excluir:
                    montos_posibles.append(monto_redondeado)

        if not montos_posibles:
            # Si no hay montos posibles, usar el método tradicional
            return self._calcular_monto_sugerido(
                operaciones_pareja, 
                rango_inicio, 
                rango_fin,
                montos_excluir
            )

        # Elegir un monto con pesos apropiados según la distribución
        if factor_riesgo < 30:
            # Para riesgo bajo, dar más peso a los montos centrales
            mid_idx = len(montos_posibles) // 2
            weights = [max(1, mid_idx - abs(i - mid_idx)) for i in range(len(montos_posibles))]
        elif factor_riesgo > 70:
            # Para riesgo alto, dar más peso a los extremos
            mid_idx = len(montos_posibles) // 2
            weights = [max(1, abs(i - mid_idx)) for i in range(len(montos_posibles))]
        else:
            # Para riesgo medio, pesos equilibrados con preferencia por valores altos
            weights = [i + 1 for i in range(len(montos_posibles))]
        
        return random.choices(montos_posibles, weights=weights, k=1)[0]
    
    def _calcular_rango_efectivo(self, rangos1, rangos2):
        """Calcula el rango efectivo entre dos conjuntos de rangos"""
        superposiciones = []
        
        for r1 in rangos1:
            for r2 in rangos2:
                inicio = max(r1['inicio'], r2['inicio'])
                fin = min(r1['fin'], r2['fin'])
                
                if fin > inicio:
                    superposiciones.append({
                        'inicio': inicio,
                        'fin': fin
                    })
        
        if not superposiciones:
            return None
        
        # Tomar el rango más amplio
        return max(superposiciones, key=lambda x: x['fin'] - x['inicio'])
    
    def obtener_detalles_emparejamiento(self, afiliado1, afiliado2, opciones=None):
        """Obtiene detalles de un emparejamiento específico"""
        try:
            opciones = opciones or {}
            incluir_historial_completo = opciones.get('incluir_historial_completo', False)
            configuracion = opciones.get('configuracion', {})
            
            # Consultar información de afiliados
            info_afiliados = db.session.query(
                RangoAfiliado.numero_afiliado,
                RangoAfiliado.recibe_en
            ).filter(
                RangoAfiliado.numero_afiliado.in_([afiliado1, afiliado2])
            ).all()
            
            if not info_afiliados:
                return {
                    "success": False,
                    "error": "No se encontraron los afiliados"
                }
            
            # Verificar si alguno usa Izipay
            usa_izipay = any(
                'Izipay' in af.recibe_en or af.recibe_en == 'Ambos'
                for af in info_afiliados
            )
            
            # Calcular rango efectivo
            rangos_a1 = RangoAfiliado.query.filter_by(numero_afiliado=afiliado1).all()
            rangos_a2 = RangoAfiliado.query.filter_by(numero_afiliado=afiliado2).all()
            
            rangos1 = [{'inicio': r.rango_inicio, 'fin': r.rango_fin} for r in rangos_a1]
            rangos2 = [{'inicio': r.rango_inicio, 'fin': r.rango_fin} for r in rangos_a2]
            
            rango_efectivo = self._calcular_rango_efectivo(rangos1, rangos2)
            
            if not rango_efectivo:
                return {
                    "success": False,
                    "error": "No hay rangos compatibles para estos afiliados"
                }
            
            rango_inicio = float(rango_efectivo['inicio'])
            rango_fin = float(rango_efectivo['fin'])
            
            # Aplicar límite de Izipay si es necesario
            if usa_izipay:
                rango_fin = min(rango_fin, 800)
            
            # Obtener historial de operaciones
            if incluir_historial_completo:
                # Obtener todas las operaciones disponibles para análisis completo
                operaciones = Operacion.query.filter(
                    ((Operacion.nombre1 == afiliado1) & (Operacion.nombre2 == afiliado2)) |
                    ((Operacion.nombre1 == afiliado2) & (Operacion.nombre2 == afiliado1))
                ).order_by(
                    Operacion.fecha.desc(), 
                    Operacion.hora
                ).all()
            else:
                # Limitar a las últimas 10 operaciones para visibilidad
                operaciones = Operacion.query.filter(
                    ((Operacion.nombre1 == afiliado1) & (Operacion.nombre2 == afiliado2)) |
                    ((Operacion.nombre1 == afiliado2) & (Operacion.nombre2 == afiliado1))
                ).order_by(
                    Operacion.fecha.desc(), 
                    Operacion.hora
                ).limit(10).all()
            
            # Convertir a formato de respuesta
            historial = [{
                'fecha': op.fecha.strftime('%Y-%m-%d'),
                'hora': op.hora.strftime('%H:%M'),
                'monto': op.monto
            } for op in operaciones]
            
            # Calcular patrón de riesgo si tenemos historial
            patron_riesgo = 0
            if historial:
                patron_riesgo = self._evaluar_patron_operaciones({
                    'historial_operaciones': historial,
                    'afiliado1': afiliado1,
                    'afiliado2': afiliado2
                })
            
            # Generar montos sugeridos adicionales
            montos_recientes = set(op.monto for op in operaciones)
            montos_sugeridos = []
            intentos = 0
            max_intentos = 20
            
            # Convertir a DataFrame para usar función existente
            df_ops = pd.DataFrame([{
                'fecha': op.fecha,
                'hora': op.hora,
                'nombre1': op.nombre1,
                'nombre2': op.nombre2,
                'monto': op.monto
            } for op in operaciones])
            
            # Usar cálculo mejorado si hay configuración
            if configuracion:
                while len(montos_sugeridos) < 5 and intentos < max_intentos:
                    monto = self._calcular_monto_sugerido_mejorado(
                        df_ops,
                        rango_inicio,
                        rango_fin,
                        patron_riesgo,
                        montos_excluir=set(montos_sugeridos + list(montos_recientes))
                    )
                    if monto is not None:
                        montos_sugeridos.append(monto)
                    intentos += 1
            else:
                while len(montos_sugeridos) < 5 and intentos < max_intentos:
                    monto = self._calcular_monto_sugerido(
                        df_ops,
                        rango_inicio,
                        rango_fin,
                        montos_excluir=set(montos_sugeridos + list(montos_recientes))
                    )
                    if monto is not None:
                        montos_sugeridos.append(monto)
                    intentos += 1
            
            return {
                "success": True,
                "data": historial,
                "montos_sugeridos": montos_sugeridos,
                "patron_riesgo": patron_riesgo,
                "usa_izipay": usa_izipay
            }
            
        except Exception as e:
            current_app.logger.error(f"Error en obtener_detalles_emparejamiento: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": f"Error obteniendo detalles: {str(e)}"
            }