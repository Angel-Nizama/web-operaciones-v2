class ValidationError(Exception):
    """Excepción para errores de validación de datos."""
    pass

class ProcessingError(Exception):
    """Excepción para errores durante el procesamiento de datos."""
    pass

class DatabaseError(Exception):
    """Excepción para errores relacionados con la base de datos."""
    pass