import uuid

from . import db


def generate_uuid():
    return str(uuid.uuid4())


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    download_url = db.Column(db.String(512), nullable=False)

    def __repr__(self):
        return f'<{self.download_url}>'
