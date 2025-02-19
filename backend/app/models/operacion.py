from datetime import datetime
from app import db

class Operacion(db.Model):
    __tablename__ = 'operaciones'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, index=True)
    hora = db.Column(db.Time, nullable=False)
    nombre1 = db.Column(db.String(50), nullable=False)
    nombre2 = db.Column(db.String(50), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<Operacion {self.id}: {self.nombre1} - {self.nombre2}>'

    def to_dict(self):
        return {
            'id': self.id,
            'fecha': self.fecha.isoformat(),
            'hora': self.hora.isoformat(),
            'nombre1': self.nombre1,
            'nombre2': self.nombre2,
            'monto': self.monto
        }