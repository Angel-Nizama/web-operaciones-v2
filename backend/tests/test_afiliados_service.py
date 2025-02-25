import os
import pytest
import tempfile
from app.services import afiliados_service
from app.models.afiliado import Afiliado

def test_buscar_afiliado(with_db_context):
    """Prueba la búsqueda de afiliados"""
    # Crear afiliados de prueba
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
    
    # Buscar por nombre
    resultados = afiliados_service.buscar_afiliado('Jua', 'nombre')
    assert len(resultados) == 1
    assert resultados[0]['numero'] == '111111111'
    
    # Buscar por número
    resultados = afiliados_service.buscar_afiliado('2222', 'numero')
    assert len(resultados) == 1
    assert resultados[0]['nombre_completo'] == 'María López Torres'
    
    # Buscar por dni
    resultados = afiliados_service.buscar_afiliado('8765', 'dni')
    assert len(resultados) == 1
    assert resultados[0]['valor_busqueda'] == '87654321'

def test_get_afiliados(with_db_context):
    """Prueba la obtención de afiliados con filtros"""
    # Crear afiliados de prueba
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
        estado='Inactivo'
    )
    
    with_db_context.session.add_all([af1, af2])
    with_db_context.session.commit()
    
    # Probar sin filtros
    resultado = afiliados_service.get_afiliados({})
    assert len(resultado['data']) == 2
    assert resultado['totalAfiliados'] == 2
    assert resultado['afiliadosActivos'] == 1
    
    # Probar con filtro de estado
    resultado = afiliados_service.get_afiliados({'estado': 'Activo'})
    assert len(resultado['data']) == 1
    assert resultado['data'][0]['numero'] == '111111111'