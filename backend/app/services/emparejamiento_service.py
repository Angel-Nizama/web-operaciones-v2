# app/services/emparejamiento_service.py
from datetime import datetime
import random
import numpy as np
import pandas as pd
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
            dias_minimos = filtros.get('dias_minimos', 1)
            riesgo_maximo = filtros.get('riesgo_maximo', 50)
            
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
            resultados = self._evaluar_emparejamientos(
                rango_afiliados,
                operaciones,
                dias_minimos,
                riesgo_maximo
            )
            
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
    
    def obtener_detalles_emparejamiento(self, afiliado1, afiliado2):
        """Obtiene detalles de un emparejamiento específico"""
        try:
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
                "usa_izipay": usa_izipay
            }
            
        except Exception as e:
            current_app.logger.error(f"Error en obtener_detalles_emparejamiento: {str(e)}")
            return {
                "success": False,
                "error": f"Error obteniendo detalles: {str(e)}"
            }