# backend/tests/conftest.py
import os
import tempfile
import pytest
from app import create_app, db
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SERVER_NAME = 'localhost.localdomain'

@pytest.fixture
def app():
    """Crear instancia de aplicación para pruebas"""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente para pruebas de API"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner para pruebas de CLI"""
    return app.test_cli_runner()

@pytest.fixture
def with_db_context(app):
    """Contexto de base de datos para pruebas"""
    with app.app_context():
        yield db