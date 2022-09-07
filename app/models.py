import uuid

from . import db


def generate_uuid():
    return str(uuid.uuid4())


class Title(db.Model):
    __tablename__ = 'titles'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<{self.name}>'
