import pytest
from datetime import datetime, timedelta, date, time
from app.services import operaciones_service, afiliados_service, emparejamiento_service
from app.models.operacion import Operacion
from app.models.afiliado import Afiliado
from app.models.rango_afiliado import RangoAfiliado

def test_emparejamiento_con_operaciones_y_afiliados(with_db_context):
    """Prueba la integración entre los tres servicios principales"""
    # 1. Crear afiliados
    af1 = Afiliado(
        numero='111111111',
        nombre='Juan',
        apellido_paterno='Pérez',
        apellido_materno='García',
        dni='12345678',
        estado='Activo'
    )
    af2 = Afiliado(
        numero='222222222',
        nombre='María',
        apellido_paterno='López',
        apellido_materno='Torres',
        dni='87654321',
        estado='Activo'
    )
    
    with_db_context.session.add_all([af1, af2])
    with_db_context.session.commit()
    
    # 2. Crear rangos para estos afiliados
    rango1 = RangoAfiliado(
        numero_afiliado='111111111',
        rango_inicio=0,
        rango_fin=500,
        recibe_en='Izipay',
        envia_a='Ambos'
    )
    rango2 = RangoAfiliado(
        numero_afiliado='222222222',
        rango_inicio=0,
        rango_fin=500,
        recibe_en='Izipay',
        envia_a='Ambos'
    )
    
    with_db_context.session.add_all([rango1, rango2])
    with_db_context.session.commit()
    
    # 3. Crear operaciones históricas
    fecha_anterior = datetime.now() - timedelta(days=30)
    op1 = Operacion(
        fecha=fecha_anterior.date(),
        hora=fecha_anterior.time(),
        nombre1='111111111',
        nombre2='222222222',
        monto=300.0
    )
    
    with_db_context.session.add(op1)
    with_db_context.session.commit()
    
    # 4. Calcular emparejamientos
    resultados = emparejamiento_service.calcular_emparejamientos({
        'dias_minimos': 1,
        'riesgo_maximo': 100
    })
    
    # 5. Verificar resultados
    assert resultados['success'] == True
    assert len(resultados['data']) > 0
    
    # Verificar que los afiliados estén en los emparejamientos
    encontrado = False
    for emparejamiento in resultados['data']:
        pareja = emparejamiento['pareja']
        if '111111111' in pareja and '222222222' in pareja:
            encontrado = True
            break
    
    assert encontrado == True
    
    # 6. Obtener detalles del emparejamiento
    detalles = emparejamiento_service.obtener_detalles_emparejamiento('111111111', '222222222')
    
    # 7. Verificar detalles
    assert detalles['success'] == True
    assert len(detalles['data']) > 0  # Historial
    assert len(detalles['montos_sugeridos']) > 0  # Montos sugeridos