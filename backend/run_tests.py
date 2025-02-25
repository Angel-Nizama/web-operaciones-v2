# backend/run_tests.py
import os
import pytest
import sys

def run_tests():
    """Ejecutar pruebas y mostrar resultados"""
    print("Ejecutando pruebas...")
    result = pytest.main(['-v', 'tests/'])
    
    if result == 0:
        print("\n✅ Todas las pruebas pasaron correctamente.")
        return True
    else:
        print("\n❌ Hay pruebas que fallaron.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)