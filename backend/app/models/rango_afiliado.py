from app import db

class RangoAfiliado(db.Model):
    __tablename__ = 'rango_afiliados'

    id = db.Column(db.Integer, primary_key=True)
    numero_afiliado = db.Column(db.String(50), db.ForeignKey('afiliados.numero'), nullable=False)
    rango_inicio = db.Column(db.Float, nullable=False)
    rango_fin = db.Column(db.Float, nullable=False)
    recibe_en = db.Column(db.String(20), nullable=False)  # 'Izipay', 'Iziya', 'Ambos'
    envia_a = db.Column(db.String(20), nullable=False)    # 'Izipay', 'Iziya', 'Ambos'

    __table_args__ = (
        db.CheckConstraint(
            "recibe_en IN ('Izipay', 'Iziya', 'Ambos')",
            name='check_recibe_en'
        ),
        db.CheckConstraint(
            "envia_a IN ('Izipay', 'Iziya', 'Ambos')",
            name='check_envia_a'
        ),
        db.Index('idx_rango_afiliados_rangos', 'rango_inicio', 'rango_fin')
    )

    def __repr__(self):
        return f'<RangoAfiliado {self.numero_afiliado}: {self.rango_inicio}-{self.rango_fin}>'

    def to_dict(self):
        return {
            'id': self.id,
            'numero_afiliado': self.numero_afiliado,
            'rango_inicio': self.rango_inicio,
            'rango_fin': self.rango_fin,
            'recibe_en': self.recibe_en,
            'envia_a': self.envia_a
        }