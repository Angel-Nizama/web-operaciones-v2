import json
import pytest
from datetime import date, time
from app.models.operacion import Operacion
from app.models.afiliado import Afiliado
from app.models.rango_afiliado import RangoAfiliado

def test_health_check(client):
    """Prueba el endpoint de health check"""
    response = client.get('/health')
    assert response.status_code == 200
    assert json.loads(response.data)['status'] == 'healthy'

def test_historico_endpoint(client, with_db_context):
    """Prueba el endpoint de histórico"""
    # Crear operación de prueba
    op = Operacion(
        fecha=date(2023, 1, 1),
        hora=time(12, 30),
        nombre1='111111111',
        nombre2='222222222',
        monto=500.0
    )
    with_db_context.session.add(op)
    with_db_context.session.commit()
    
    # Hacer solicitud
    response = client.post('/api/historico', 
                       json={},
                       content_type='application/json')
    
    # Verificar respuesta
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert len(data['data']) == 1
    assert data['total'] == 1

def test_afiliados_endpoint(client, with_db_context):
    """Prueba el endpoint de afiliados"""
    # Crear afiliado de prueba
    af = Afiliado(
        numero='111111111',
        nombre='Juan',
        apellido_paterno='Pérez',
        apellido_materno='García',
        dni='12345678',
        estado='Activo'
    )
    with_db_context.session.add(af)
    with_db_context.session.commit()
    
    # Hacer solicitud
    response = client.post('/api/afiliados', 
                       json={},
                       content_type='application/json')
    
    # Verificar respuesta
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert len(data['data']) == 1
    assert data['totalAfiliados'] == 1

def test_emparejador_endpoint(client, with_db_context):
    """Prueba el endpoint de emparejador"""
    # Crear afiliados y rangos
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
    
    with_db_context.session.add_all([af1, af2, rango1, rango2])
    with_db_context.session.commit()
    
    # Hacer solicitud
    response = client.post('/api/emparejador/calcular', 
                       json={'dias_minimos': 1, 'riesgo_maximo': 100},
                       content_type='application/json')
    
    # Verificar respuesta
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True