from sqlalchemy import func

from . import db


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    host = db.Column(db.String(64), nullable=False)
    is_ok = db.Column(db.Boolean, nullable=False, default=False)
    content = db.Column(db.String(512), nullable=False, default=None)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'{self.id}) [{self.content}'
