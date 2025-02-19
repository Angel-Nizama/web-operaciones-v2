from app import db

class Afiliado(db.Model):
    __tablename__ = 'afiliados'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido_paterno = db.Column(db.String(100), nullable=False)
    apellido_materno = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120))
    estado = db.Column(db.String(20), nullable=False, default='Inactivo')
    
    # Relación con rangos
    rangos = db.relationship('RangoAfiliado', backref='afiliado', lazy='dynamic')

    def __repr__(self):
        return f'<Afiliado {self.numero}: {self.nombre} {self.apellido_paterno}>'

    def to_dict(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'nombre': self.nombre,
            'apellido_paterno': self.apellido_paterno,
            'apellido_materno': self.apellido_materno,
            'dni': self.dni,
            'email': self.email,
            'estado': self.estado
        }