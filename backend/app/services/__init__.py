from app.services.operaciones_service import OperacionesService
from app.services.afiliados_service import AfiliadosService
from app.services.emparejamiento_service import EmparejamientoService
from app.services.base_service import BaseService

# Crear instancias de servicios
operaciones_service = OperacionesService()
afiliados_service = AfiliadosService()
emparejamiento_service = EmparejamientoService()