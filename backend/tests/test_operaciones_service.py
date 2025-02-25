import os
import pytest
import tempfile
import pandas as pd
from datetime import datetime
from app.services import operaciones_service
from app.models.operacion import Operacion

def test_allowed_file(app):
    """Prueba la validación de archivos"""
    with app.app_context():
        assert operaciones_service.allowed_file('archivo.xlsx') == True
        assert operaciones_service.allowed_file('archivo.xls') == True
        assert operaciones_service.allowed_file('archivo.csv') == True
        assert operaciones_service.allowed_file('archivo.txt') == False
        assert operaciones_service.allowed_file('') == False
        assert operaciones_service.allowed_file(None) == False

def test_process_excel_file(app):
    """Prueba el procesamiento de archivos Excel"""
    # Crear archivo temporal para prueba
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp:
        temp.write(b"Date,Time,Phone Number 1,Phone Number 2,Amount\n")
        temp.write(b"2023-01-01,12:30,123456789,987654321,500.50\n")
        temp_path = temp.name
    
    try:
        # Procesar archivo
        with app.app_context():
            df = operaciones_service.process_excel_file(temp_path)
            
            # Verificar resultados
            assert len(df) == 1
            assert df.iloc[0]['Date'] == '2023-01-01'
            assert df.iloc[0]['Time'] == '12:30'
            assert str(df.iloc[0]['Phone Number 1']) == '123456789'
            assert str(df.iloc[0]['Phone Number 2']) == '987654321'
            assert df.iloc[0]['Amount'] == 500.50
    finally:
        # Limpiar
        os.unlink(temp_path)

def test_get_historico(with_db_context):
    """Prueba la obtención de histórico de operaciones"""
    from datetime import datetime, date, time
    
    # Crear operaciones de prueba
    op1 = Operacion(
        fecha=date(2023, 1, 1),
        hora=time(12, 30),
        nombre1='111111111',
        nombre2='222222222',
        monto=500.0
    )
    op2 = Operacion(
        fecha=date(2023, 1, 2),
        hora=time(14, 45),
        nombre1='111111111',
        nombre2='333333333',
        monto=700.0
    )
    
    with_db_context.session.add_all([op1, op2])
    with_db_context.session.commit()
    
    # Probar sin filtros
    resultado = operaciones_service.get_historico({})
    assert len(resultado['data']) == 2
    assert resultado['total'] == 2
    assert resultado['montoTotal'] == 1200.0
    
    # Probar con filtro de nombre
    resultado = operaciones_service.get_historico({'nombre1': '111111111'})
    assert len(resultado['data']) == 2
    
    # Probar con filtro de fecha
    resultado = operaciones_service.get_historico({'fecha_desde': '2023-01-02'})
    assert len(resultado['data']) == 1
    assert resultado['data'][0]['nombre1'] == '111111111'
    assert resultado['data'][0]['nombre2'] == '333333333'